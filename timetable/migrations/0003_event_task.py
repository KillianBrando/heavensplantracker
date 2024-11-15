# Generated by Django 5.0.2 on 2024-09-18 16:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0002_alter_event_recurring_option'),
        ('todo', '0008_task_completed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='task',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='todo.task'),
        ),
    ]
