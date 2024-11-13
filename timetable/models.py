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
    task = models.OneToOneField('todo.Task', on_delete=models.CASCADE, null=True, blank=True)
    is_task = models.BooleanField(default=False)
    recurring_option = models.CharField(
        max_length=10, choices=RecurringOption.choices, default=RecurringOption.NONE
    )

    def get_next_occurrences(self, from_date=None, num_occurrences=5):
        if from_date is None:
            from_date = timezone.now()

        occurrences = []
        current_occurrence = self.start_time

        delta = {
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'monthly': relativedelta(months=1)
        }.get(self.recurring_option, None)

        if delta:
            while len(occurrences) < num_occurrences:
                if current_occurrence >= from_date:
                    occurrences.append(current_occurrence)
                current_occurrence += delta

        return occurrences

    def __str__(self):
        return self.title

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("The event end time must be after the start time.")
        if self.start_time < timezone.now():
            raise ValidationError("The event start time cannot be in the past.")