# Generated by Django 4.2.11 on 2024-03-30 12:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appusers', '0003_remove_localwithdrawal_pin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transactionhistory',
            old_name='timestamp',
            new_name='time',
        ),
    ]