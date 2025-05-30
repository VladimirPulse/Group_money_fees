# Generated by Django 5.2 on 2025-04-23 18:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "money_fees",
            "0008_alter_collect_options_alter_payment_options_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="collect",
            name="collec_fees",
        ),
        migrations.AddField(
            model_name="payment",
            name="collec_fees",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="money_fees.collect",
            ),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="CollectUser",
        ),
    ]
