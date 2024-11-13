from django.apps import apps
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    RECURRING_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    recurring = models.CharField(max_length=10, choices=RECURRING_CHOICES, default='none')
    order = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def clean(self):
        if self.due_date and self.due_date < now().date():
            raise ValidationError("Due date cannot be in the past")

    def get_next_due_date(self):
        if not self.due_date:
            return None

        recurrence_delta = {
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'monthly': relativedelta(months=1)
        }.get(self.recurring, None)

        return self.due_date + recurrence_delta if recurrence_delta else None

    def to_event(self):
        if self.due_date:
            Event = apps.get_model('timetable', 'Event')
            try:
                Event.objects.create(
                    user=self.user,
                    title=self.title,
                    start_time=self.due_date,
                    end_time=self.due_date + timedelta(hours=1),
                    description=self.description,
                    task=self,
                    is_task=True
                )
            except Exception as e:
                raise ValidationError(f"Failed to convert task to event: {str(e)}")