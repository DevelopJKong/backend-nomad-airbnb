# Generated by Django 4.2.5 on 2024-09-16 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="booking",
            old_name="experiences",
            new_name="experience",
        ),
    ]
