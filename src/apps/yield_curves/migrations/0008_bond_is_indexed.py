# Generated by Django 5.2.1 on 2025-06-10 21:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("yield_curves", "0007_bond_is_green"),
    ]

    operations = [
        migrations.AddField(
            model_name="bond",
            name="is_indexed",
            field=models.BooleanField(default=False),
        ),
    ]
