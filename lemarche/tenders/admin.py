from datetime import datetime

from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django_admin_filters import MultiChoice
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from lemarche.common.admin import admin_site
from lemarche.perimeters.admin import PerimeterRegionFilter
from lemarche.tenders import constants
from lemarche.tenders.forms import TenderAdminForm
from lemarche.tenders.models import PartnerShareTender, Tender
from lemarche.utils.fields import pretty_print_readonly_jsonfield
from lemarche.www.tenders.tasks import (
    send_confirmation_published_email_to_author,
    send_tender_emails_to_partners,
    send_tender_emails_to_siaes,
)


class ScaleMarcheUselessFilter(MultiChoice):
    FILTER_LABEL = "Utilité du marché de l'inclusion"
    BUTTON_LABEL = "Appliquer"


class KindFilter(MultiChoice):
    FILTER_LABEL = "Type de besoin"
    BUTTON_LABEL = "Appliquer"


class ResponseKindFilter(admin.SimpleListFilter):
    title = Tender._meta.get_field("response_kind").verbose_name
    parameter_name = "response_kind"

    def lookups(self, request, model_admin):
        return Tender.RESPONSE_KIND_CHOICES

    def queryset(self, request, queryset):
        lookup_value = self.value()
        if lookup_value:
            queryset = queryset.filter(response_kind__contains=[lookup_value])
        return queryset


def update_and_send_tender_task(tender: Tender):
    # 1) validate the tender
    tender.set_validated(with_save=True)
    # 2) find the matching Siaes? done in Tender post_save signal
    send_confirmation_published_email_to_author(tender, nb_matched_siaes=tender.siaes.count())
    # 3) send the tender to all matching Siaes & Partners
    send_tender_emails_to_siaes(tender)
    send_tender_emails_to_partners(tender)


def restart_send_tender_task(tender: Tender):
    # 1) log the tender send restart
    log_item = {
        "action": "restart_send",
        "date": str(datetime.now()),
    }
    tender.logs.append(log_item)
    tender.save()
    # 2) send the tender to all matching Siaes & Partners
    send_tender_emails_to_siaes(tender)
    send_tender_emails_to_partners(tender)


@admin.register(Tender, site=admin_site)
class TenderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "status",
        "is_validate",
        "title",
        "user_with_link",
        "kind",
        "deadline_date",
        "start_working_date",
        "siae_count_with_link",
        # "siae_email_send_count_with_link",
        "siae_email_link_click_count_with_link",
        "siae_detail_display_count_with_link",
        "siae_detail_contact_click_count_with_link",
        "siae_transactioned",
        "created_at",
        "validated_at",
    ]

    list_filter = [
        ("kind", KindFilter),
        "status",
        ("scale_marche_useless", ScaleMarcheUselessFilter),
        "deadline_date",
        "start_working_date",
        ResponseKindFilter,
        "siae_transactioned",
    ]
    advanced_filter_fields = (
        "kind",
        "status",
        "scale_marche_useless",
        "deadline_date",
        "start_working_date",
    )
    # filter on "perimeters"? (loads ALL the perimeters... Use django-admin-autocomplete-filter instead?)
    search_fields = ["id", "title", "author__id", "author__email"]
    search_help_text = "Cherche sur les champs : ID, Titre, Auteur (ID, E-mail)"
    ordering = ["-created_at"]

    autocomplete_fields = ["sectors", "location", "perimeters", "author"]
    readonly_fields = [field.name for field in Tender._meta.fields if field.name.endswith("_last_seen_date")] + [
        # slug
        # status
        "validated_at",
        "siae_count_with_link",
        "siae_email_send_count_with_link",
        "siae_email_link_click_count_with_link",
        "siae_detail_display_count_with_link",
        "siae_detail_contact_click_count_with_link",
        "logs_display",
        "extra_data_prettier",
        "created_at",
        "updated_at",
    ]
    formfield_overrides = {models.TextField: {"widget": CKEditorWidget}}

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "slug", "kind"),
            },
        ),
        (
            "Détails",
            {
                "fields": (
                    "description",
                    "constraints",
                    "external_link",
                    "accept_cocontracting",
                ),
            },
        ),
        (
            "Filtres",
            {
                "fields": (
                    "siae_kind",
                    "sectors",
                    "presta_type",
                )
            },
        ),
        (
            "Lieux d'exécution 'France entière'",
            {
                "fields": ("is_country_area",),
            },
        ),
        (
            "Lieux d'exécution 'spécifique'",
            {
                "fields": (
                    "location",
                    "perimeters",
                    "include_country_area",
                ),
            },
        ),
        (
            "Montant",
            {
                "fields": (
                    "amount",
                    "why_amount_is_blank",
                    "accept_share_amount",
                ),
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "deadline_date",
                    "start_working_date",
                ),
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "author",
                    "contact_first_name",
                    "contact_last_name",
                    "contact_email",
                    "contact_phone",
                    "response_kind",
                ),
            },
        ),
        (
            "Structures",
            {
                "fields": (
                    "siae_count_with_link",
                    "siae_email_send_count_with_link",
                    "siae_email_link_click_count_with_link",
                    "siae_detail_display_count_with_link",
                    "siae_detail_contact_click_count_with_link",
                    "siae_transactioned",
                )
            },
        ),
        (
            "Utilité du marché de l'inclusion",
            {
                "fields": (
                    "scale_marche_useless",
                    "marche_benefits",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "validated_at",
                )
            },
        ),
        (
            "Stats et autres",
            {
                "fields": (
                    "siae_list_last_seen_date",
                    "source",
                    "logs_display",
                    "extra_data_prettier",
                ),
            },
        ),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )

    change_form_template = "tenders/admin_change_form.html"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.with_siae_stats()
        return qs

    def get_changeform_initial_data(self, request):
        """
        Default values in add form.
        """
        return {"source": Tender.SOURCE_STAFF_C4_CREATED}

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in [
            "tendersiae__email_send_date__isnull",
            "tendersiae__email_link_click_date__isnull",
            "tendersiae__detail_display_date__isnull",
            "tendersiae__detail_contact_click_date__isnull",
        ]:
            return True
        return super().lookup_allowed(lookup, *args, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:
            # add status in read only when the tender is not owned by the current user
            if obj.author_id and obj.author_id != request.user.id:
                readonly_fields.append("status")
            # slug cannot be changed once the tender is validated
            if obj.status == constants.STATUS_VALIDATED:
                readonly_fields.append("slug")
        return readonly_fields

    def save_model(self, request, obj: Tender, form, change):
        if not obj.id and not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def is_validate(self, tender: Tender):
        return tender.validated_at is not None

    is_validate.boolean = True
    is_validate.short_description = "Validé"

    def user_with_link(self, tender):
        url = reverse("admin:users_user_change", args=[tender.author_id])
        return format_html(f'<a href="{url}">{tender.author}</a>')

    user_with_link.short_description = "Auteur"
    user_with_link.admin_order_field = "author"

    def siae_count_with_link(self, tender):
        url = reverse("admin:siaes_siae_changelist") + f"?tenders__in={tender.id}"
        return format_html(f'<a href="{url}">{getattr(tender, "siae_count", 0)}</a>')

    siae_count_with_link.short_description = "Structures concernées"
    siae_count_with_link.admin_order_field = "siae_count"

    def siae_email_send_count_with_link(self, tender):
        url = (
            reverse("admin:siaes_siae_changelist")
            + f"?tenders__in={tender.id}&tendersiae__email_send_date__isnull=False"
        )
        return format_html(f'<a href="{url}">{getattr(tender, "siae_email_send_count", 0)}</a>')

    siae_email_send_count_with_link.short_description = "S. contactées"
    siae_email_send_count_with_link.admin_order_field = "siae_email_send_count"

    def siae_email_link_click_count_with_link(self, tender):
        url = (
            reverse("admin:siaes_siae_changelist")
            + f"?tenders__in={tender.id}&tendersiae__email_link_click_date__isnull=False"
        )
        return format_html(f'<a href="{url}">{getattr(tender, "siae_email_link_click_count", 0)}</a>')

    siae_email_link_click_count_with_link.short_description = "S. cliquées"
    siae_email_link_click_count_with_link.admin_order_field = "siae_email_link_click_count"

    def siae_detail_display_count_with_link(self, tender):
        url = (
            reverse("admin:siaes_siae_changelist")
            + f"?tenders__in={tender.id}&tendersiae__detail_display_date__isnull=False"
        )
        return format_html(f'<a href="{url}">{getattr(tender, "siae_detail_display_count", 0)}</a>')

    siae_detail_display_count_with_link.short_description = "S. vues"
    siae_detail_display_count_with_link.admin_order_field = "siae_detail_display_count"

    def siae_detail_contact_click_count_with_link(self, tender):
        url = (
            reverse("admin:siaes_siae_changelist")
            + f"?tenders__in={tender.id}&tendersiae__detail_contact_click_date__isnull=False"
        )
        return format_html(f'<a href="{url}">{getattr(tender, "siae_detail_contact_click_count", 0)}</a>')

    siae_detail_contact_click_count_with_link.short_description = "S. intéressées"
    siae_detail_contact_click_count_with_link.admin_order_field = "siae_detail_contact_click_count"

    def logs_display(self, tender=None):
        if tender:
            return pretty_print_readonly_jsonfield(tender.logs)
        return "-"

    logs_display.short_description = Tender._meta.get_field("logs").verbose_name

    def response_change(self, request, obj: Tender):
        if request.POST.get("_validate_tender"):
            update_and_send_tender_task(tender=obj)
            self.message_user(request, "Ce dépôt de besoin a été validé et envoyé aux structures")
            return HttpResponseRedirect(".")
        elif request.POST.get("_restart_tender"):
            restart_send_tender_task(tender=obj)
            self.message_user(request, "Ce dépôt de besoin a été renvoyé aux structures")
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

    def extra_data_prettier(self, instance: Tender = None):
        if instance:
            return pretty_print_readonly_jsonfield(instance.extra_data)
        return "-"

    extra_data_prettier.short_description = Tender._meta.get_field("extra_data").verbose_name


@admin.register(PartnerShareTender, site=admin_site)
class PartnerShareTenderAdmin(admin.ModelAdmin, DynamicArrayMixin):
    form = TenderAdminForm
    list_display = ["id", "name", "perimeters_string", "amount_in", "created_at"]
    list_filter = [PerimeterRegionFilter, "amount_in"]
    search_fields = ["id", "name"]
    search_help_text = "Cherche sur les champs : ID, Nom"

    readonly_fields = ["perimeters_string", "logs_display", "created_at", "updated_at"]
    autocomplete_fields = ["perimeters"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("perimeters")
        return qs

    def perimeters_string(self, partnersharetender):
        return partnersharetender.perimeters_list_string

    perimeters_string.short_description = "Périmètres"

    def logs_display(self, partnersharetender=None):
        if partnersharetender:
            return pretty_print_readonly_jsonfield(partnersharetender.logs)
        return "-"

    logs_display.short_description = PartnerShareTender._meta.get_field("logs").verbose_name
