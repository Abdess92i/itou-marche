# Generated by Django 4.0.7 on 2022-10-13 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="articlepage",
            name="with_cta_tender",
            field=models.BooleanField(default=False, verbose_name="avec un CTA pour les besoins ?"),
        ),
    ]
