from django.apps import apps
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta

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
    recurring = models.CharField(max_length=10, choices=RECURRING_CHOICES, default='none')  # Recurring option
    order = models.IntegerField(default=0)  # Field to store the order of tasks
    completed_at = models.DateTimeField(null=True, blank=True)  # Track when the task was completed

    def __str__(self):
        return self.title

    def clean(self):
        # Ensure due_date is not in the past
        if self.due_date and self.due_date < now().date():
            raise ValidationError("Due date cannot be in the past")

    def get_next_due_date(self):
        """Returns the next due date based on the task's recurrence."""
        if self.recurring == 'daily':
            return self.due_date + timedelta(days=1)
        elif self.recurring == 'weekly':
            return self.due_date + timedelta(weeks=1)
        elif self.recurring == 'monthly':
            return self.due_date + timedelta(days=30)
        return None

    def to_event(self):
        """Convert the task into a calendar event."""
        if self.due_date:
            Event = apps.get_model('timetable', 'Event')  # Use apps.get_model instead of models.get_model
            Event.objects.create(
                user=self.user,
                title=self.title,
                start_time=self.due_date,  # Example: Task's due date as the event's start
                end_time=self.due_date + timedelta(hours=1),  # Assuming 1-hour duration for the event
                description=self.description,
                task=self,  # Link the event to the task
                is_task=True  # Mark this event as a task
            )
