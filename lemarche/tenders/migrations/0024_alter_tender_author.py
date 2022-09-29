# Generated by Django 4.0.7 on 2022-09-29 16:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tenders", "0023_alter_partnersharetender_amount_in_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tender",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tenders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Auteur",
            ),
        ),
    ]
