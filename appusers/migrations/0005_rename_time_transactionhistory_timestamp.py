# Generated by Django 4.2.11 on 2024-03-30 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appusers', '0004_rename_timestamp_transactionhistory_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transactionhistory',
            old_name='time',
            new_name='timestamp',
        ),
    ]
