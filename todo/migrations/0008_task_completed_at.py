# Generated by Django 5.0.2 on 2024-09-17 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0007_task_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]