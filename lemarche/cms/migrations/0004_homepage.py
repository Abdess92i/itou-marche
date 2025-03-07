# Generated by Django 4.1.6 on 2023-03-15 16:32

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


def remove_homepage(apps, schema_editor):
    Homepage = apps.get_model("cms", "homepage")
    # need to delete first the homepage, go to scripts/create_wagtail_homepage.py
    # comment above line (after script delete) to downgrade the migration
    Homepage.objects.first().delete()


def create_homepage(apps, schema_editor):
    # use script scripts/create_wagtail_homepage.py
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0083_workflowcontenttype"),
        ("cms", "0003_advert"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "banner_title",
                    models.CharField(
                        default="Votre recherche de prestataires inclusifs est chronophage ?", max_length=120
                    ),
                ),
                (
                    "banner_subtitle",
                    models.CharField(
                        blank=True, default="Confiez votre sourcing au marché de l'inclusion !", max_length=120
                    ),
                ),
                (
                    "banner_arguments_list",
                    wagtail.fields.StreamField([("item", wagtail.blocks.CharBlock())], use_json_field=True),
                ),
                (
                    "banner_cta_id",
                    models.SlugField(
                        allow_unicode=True,
                        default="home-demande",
                        help_text="id du call to action (pour le suivi)",
                        max_length=255,
                        verbose_name="slug",
                    ),
                ),
                (
                    "banner_cta_text",
                    models.CharField(
                        default="Publier un besoin d'achat", max_length=255, verbose_name="Titre du call to action"
                    ),
                ),
                (
                    "content",
                    wagtail.fields.StreamField(
                        [
                            ("website_stats", wagtail.blocks.StructBlock([])),
                            (
                                "section_they_publish_tenders",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(
                                                default="Ils ont publié un besoin sur le marché",
                                                max_length=120,
                                                required=True,
                                            ),
                                        )
                                    ]
                                ),
                            ),
                            (
                                "section_studies_cases_tenders",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(
                                                default="100% des besoins ont reçu des réponses en 24h",
                                                max_length=120,
                                                required=True,
                                            ),
                                        ),
                                        (
                                            "subtitle",
                                            wagtail.blocks.CharBlock(
                                                default="Gagnez du temps en utilisant le marché.",
                                                max_length=120,
                                                required=True,
                                            ),
                                        ),
                                    ]
                                ),
                            ),
                            (
                                "section_our_siaes",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "subtitle",
                                            wagtail.blocks.RichTextBlock(
                                                default="\n            Faire appel à nos 8500 prestataires inclusifs, c'est la garantie d'être accompagné\n            par des professionnels reconnus et certifiés dans leur domaine.\n        ",  # noqa
                                                features=["bold", "italic"],
                                                required=True,
                                            ),
                                        )
                                    ]
                                ),
                            ),
                            (
                                "section_our_ressources",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(
                                                default="Nos ressources", max_length=120, required=True
                                            ),
                                        )
                                    ]
                                ),
                            ),
                            (
                                "section_what_find_here",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(
                                                default="Sur le marché", max_length=120, required=True
                                            ),
                                        )
                                    ]
                                ),
                            ),
                            (
                                "section_our_partners",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(
                                                default="Nos ressources", max_length=120, required=True
                                            ),
                                        )
                                    ]
                                ),
                            ),
                        ],
                        blank=True,
                        null=True,
                        use_json_field=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
        migrations.RunPython(code=create_homepage, reverse_code=remove_homepage),
    ]
