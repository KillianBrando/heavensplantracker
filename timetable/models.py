from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

class Event(models.Model):
    class RecurringOption(models.TextChoices):
        NONE = 'none', 'None'
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    task = models.OneToOneField('todo.Task', on_delete=models.CASCADE, null=True, blank=True)  # Lazy reference to Task
    is_task = models.BooleanField(default=False)
    recurring_option = models.CharField(
        max_length=10, choices=RecurringOption.choices, default=RecurringOption.NONE
    )

    def get_next_occurrences(self, from_date=None, num_occurrences=5):
        """Return the next occurrences of a recurring event."""
        if from_date is None:
            from_date = timezone.now()

        occurrences = []
        current_occurrence = self.start_time

        delta = None
        if self.recurring_option == 'daily':
            delta = timedelta(days=1)
        elif self.recurring_option == 'weekly':
            delta = timedelta(weeks=1)
        elif self.recurring_option == 'monthly':
            delta = relativedelta(months=1)

        if delta:
            for _ in range(num_occurrences):
                if current_occurrence >= from_date:
                    occurrences.append(current_occurrence)
                current_occurrence += delta

        return occurrences

    def __str__(self):
        return self.title

    def clean(self):
        """Ensure that start_time is before end_time."""
        if self.start_time >= self.end_time:
            raise ValidationError("The event end time must be after the start time.")
