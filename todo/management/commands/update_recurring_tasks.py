# todo/management/commands/update_recurring_tasks.py

from django.core.management.base import BaseCommand
from todo.models import Task
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create recurring tasks based on their recurrence settings.'

    def handle(self, *args, **kwargs):
        now = timezone.now().date()
        tasks = Task.objects.filter(recurring__in=['daily', 'weekly', 'monthly'], due_date__lte=now, status='pending')
        
        for task in tasks:
            next_due_date = task.get_next_due_date()
            if next_due_date:
                # Create a duplicate of the task with the next due date
                Task.objects.create(
                    user=task.user,
                    title=task.title,
                    description=task.description,
                    priority=task.priority,
                    due_date=next_due_date,
                    status='pending',
                    recurring=task.recurring
                )
                self.stdout.write(self.style.SUCCESS(f'Created recurring task: {task.title} with due date: {next_due_date}'))
