# Generated by Django 5.1.1 on 2024-09-25 05:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('first_app', '0004_rename_established_date_publisher_register_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publisher',
            old_name='register_date',
            new_name='established_date',
        ),
    ]
