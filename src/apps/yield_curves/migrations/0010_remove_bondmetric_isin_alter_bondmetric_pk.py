# Generated by Django 5.2.1 on 2025-06-17 20:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("yield_curves", "0009_remove_analysis_is_deleted"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bondmetric",
            name="isin",
        ),
        migrations.AlterField(
            model_name="bondmetric",
            name="pk",
            field=models.CompositePrimaryKey(
                "date", "bond_id", blank=True, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]
