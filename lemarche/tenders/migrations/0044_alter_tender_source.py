# Generated by Django 4.1.7 on 2023-03-16 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0043_rename_tender_siae_interested_list_last_seen_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tender",
            name="source",
            field=models.CharField(
                choices=[
                    ("FORM", "Formulaire"),
                    ("FORM_CSRF", "Formulaire (erreur CSRF)"),
                    ("STAFF_C4_CREATED", "Staff Marché (via l'Admin)"),
                    ("API", "API"),
                ],
                default="FORM",
                max_length=20,
                verbose_name="Source",
            ),
        ),
    ]
