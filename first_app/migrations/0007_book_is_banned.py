# Generated by Django 5.1 on 2024-10-07 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first_app', '0006_genre_book_genre'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='is_banned',
            field=models.BooleanField(default=False),
        ),
    ]
