# Generated by Django 4.0.7 on 2022-10-11 12:39

from django.db import migrations, models

import lemarche.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0025_alter_tender_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="tender",
            name="is_marche_useful",
            field=models.BooleanField(
                default=True,
                help_text="Pour ce besoin, auriez-vous fait appel à des prestataires inclusifs si le Marché de l'inclusion n'existait pas ?",  # noqa
                verbose_name="Utilité du marché de l'inclusion",
            ),
        ),
        migrations.AddField(
            model_name="tender",
            name="marche_benefits",
            field=lemarche.utils.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("TIME", "Gagner du temps"),
                        ("DISCOVER", "Découvrir de nouveaux prestataires inclusifs"),
                        ("MORE", "Faire plus d'achats inclusifs"),
                        ("ASSIGN", "Attribuer une clause sociale à un marché "),
                        ("NONE", "Aucun"),
                    ],
                    max_length=20,
                ),
                blank=True,
                default=list,
                help_text="Quels sont le(s) bénéfice(s) de passer par le Marché de l'inclusion pour ce besoin ?",
                size=None,
                verbose_name="Bénéfices du marché de l'inclusion",
            ),
        ),
    ]
