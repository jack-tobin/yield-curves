# Generated by Django 5.2.1 on 2025-06-01 17:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("yield_curves", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="bond",
            name="issue_volume",
            field=models.DecimalField(decimal_places=4, max_digits=16, null=True),
        ),
    ]
