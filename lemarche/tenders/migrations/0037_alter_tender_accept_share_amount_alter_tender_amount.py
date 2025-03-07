# Generated by Django 4.1.3 on 2022-12-07 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0036_tender_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tender",
            name="accept_share_amount",
            field=models.BooleanField(
                default=False,
                help_text="Je souhaite partager ce montant aux prestataires inclusifs recevant mon besoin",
                verbose_name="Partage du montant du besoin",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="amount",
            field=models.CharField(
                blank=True,
                choices=[
                    ("0-1K", "0-1000 €"),
                    ("1-5K", "1-5 K€"),
                    ("5-10K", "5-10 K€"),
                    ("10-15K", "10-15 K€"),
                    ("15-20K", "15-20 K€"),
                    ("20-30K", "20-30 K€"),
                    ("30-50K", "30-50 K€"),
                    ("50-100K", "50-100 K€"),
                    ("100-150K", "100-150 K€"),
                    ("150-250K", "150-250 K€"),
                    ("250-500K", "250-500 K€"),
                    ("500-750K", "500-750 K€"),
                    ("750K-1M", "750-1000 K€"),
                    (">1M", "> 1 M€"),
                ],
                help_text="Sélectionnez le montant reservé aux structures d'insertion et/ou de handicap",
                max_length=9,
                null=True,
                verbose_name="Montant du besoin",
            ),
        ),
    ]
