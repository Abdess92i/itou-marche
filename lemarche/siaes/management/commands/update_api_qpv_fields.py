import argparse
from datetime import timedelta

import requests
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from lemarche.siaes.models import Siae
from lemarche.utils.apis import api_slack
from lemarche.utils.apis.api_qpv import IS_QPV_KEY, QPV_CODE_KEY, QPV_NAME_KEY, get_default_client, is_in_qpv
from lemarche.utils.commands import BaseCommand


class Command(BaseCommand):
    """
    Populates API QPV

    Note: Only on Siae who have coords, filter only on Siae not updated by the API since a two months

    Usage: poetry run python manage.py update_api_qpv_fields
    Usage: poetry run python manage.py update_api_qpv_fields --limit 10
    Usage: poetry run python manage.py update_api_qpv_fields --force
    Usage: poetry run python manage.py update_api_qpv_fields --limit 100 --no-force
    """

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self.success_count = {"etablissement": 0, "etablissement_qpv": 0}

    FIELDS_TO_BULK_UPDATE = ["is_qpv", "api_qpv_last_sync_date", "qpv_code", "qpv_name"]

    def add_arguments(self, parser):
        parser.add_argument(
            "-L", "--limit", type=int, default=None, help="Limiter le nombre de structures à processer"
        )
        parser.add_argument(
            "-F",
            "--force",
            action=argparse.BooleanOptionalAction,
            default=None,
            help="Forcer l'update sans la vérification de la dernière mise à jour",
        )

    def get_query_set(self, **options):
        siaes_queryset = Siae.objects.filter(Q(coords__isnull=False)).order_by("id")

        if not options["force"]:
            since_last_date_limit = timezone.now() - timedelta(days=settings.API_QPV_RELATIVE_DAYS_TO_UPDATE)
            siaes_queryset = siaes_queryset.filter(
                (Q(api_qpv_last_sync_date__lte=since_last_date_limit) | Q(api_qpv_last_sync_date__isnull=True))
            )

        if options["limit"]:
            siaes_queryset = siaes_queryset[: options["limit"]]
        return siaes_queryset

    def handle(self, *args, **options):
        siae_list = self.get_query_set(**options)
        self.stdout_messages_info(["Populating API QPV...", f"Found {len(siae_list)} Siae"])

        count_siae_to_update = 0
        client = get_default_client()
        try:
            siaes_to_update = []
            for siae in siae_list:
                # update siae from API
                siae = self.update_siae(client, siae)
                siaes_to_update.append(siae)
                # log progress
                count_siae_to_update = len(siaes_to_update)
                if (count_siae_to_update % 50) == 0:
                    self.stdout_info(f"{count_siae_to_update}...")

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 429:
                # the real exceed request error have code=10005, with the api
                # but requests send error code 429 "Unknown Status Code"
                self.stdout_error("exceeded the requests limit for today (5000/per day)")
        finally:
            client.close()
            # we still save siaes qpv status
            Siae.objects.bulk_update(
                siaes_to_update, self.FIELDS_TO_BULK_UPDATE, batch_size=settings.BATCH_SIZE_BULK_UPDATE
            )

        msg_success = [
            "----- Recap: sync API QPV -----",
            f"Done! Processed {len(siaes_to_update)}/{len(siae_list)} siaes",
            f"success count: {self.success_count['etablissement']}/{len(siaes_to_update)}",
            f"True count: {self.success_count['etablissement_qpv']}/{len(siaes_to_update)}",
        ]
        self.stdout_messages_success(msg_success)
        api_slack.send_message_to_channel("\n".join(msg_success))

    def update_siae(self, client, siae):
        # call api is in qpv
        result_is_in_qpv = is_in_qpv(siae.latitude, siae.longitude, client=client)
        self.success_count["etablissement"] += 1
        siae.is_qpv = result_is_in_qpv[IS_QPV_KEY]
        siae.api_qpv_last_sync_date = timezone.now()
        if siae.is_qpv:
            siae.qpv_code = result_is_in_qpv[QPV_CODE_KEY]
            siae.qpv_name = result_is_in_qpv[QPV_NAME_KEY]
            self.success_count["etablissement_qpv"] += 1
        else:
            siae.qpv_code = ""
            siae.qpv_name = ""
        return siae
