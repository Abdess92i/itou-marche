# Generated by Django 4.1.3 on 2022-11-24 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0032_tender_extra_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="tender",
            name="include_country_area",
            field=models.BooleanField(
                default=False,
                help_text="Laisser vide pour exclure les structures qui ont comme périmètre d'intervention 'France entière'",  # noqa
                verbose_name="Inclure les structures qui ont comme périmètre d'intervention 'France entière' ?",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="is_country_area",
            field=models.BooleanField(
                default=False,
                help_text="Retournera uniquement les structures qui ont comme périmètre d'intervention 'France entière'",  # noqa
                verbose_name="France entière",
            ),
        ),
    ]
