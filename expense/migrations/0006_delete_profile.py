# Generated by Django 5.0.2 on 2024-09-15 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0005_profile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Profile',
        ),
    ]