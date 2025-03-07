# Generated by Django 4.0.7 on 2022-09-05 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tracker",
            fields=[
                ("id_internal", models.AutoField(primary_key=True, serialize=False)),
                ("version", models.PositiveIntegerField(verbose_name="Version")),
                ("date_created", models.DateTimeField(verbose_name="Timestamp (UNIX Epoch)")),
                ("send_order", models.PositiveIntegerField(default=0)),
                ("env", models.CharField(max_length=200)),
                ("source", models.CharField(max_length=200)),
                ("session_id", models.UUIDField(verbose_name="browser session UUID")),
                ("page", models.CharField(max_length=200)),
                ("action", models.CharField(max_length=200, verbose_name="Type d'action")),
                ("data", models.JSONField()),
                ("isadmin", models.BooleanField(default=False)),
            ],
            options={
                "db_table": "trackers",
            },
        ),
    ]
