# Generated by Django 5.2 on 2025-05-21 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("money_fees", "0010_alter_payment_collec_fees"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collect",
            name="image",
            field=models.ImageField(
                blank=True, default=None, null=True, upload_to="images/"
            ),
        ),
    ]
