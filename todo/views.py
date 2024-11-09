from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from .forms import TaskForm
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, F
from django.db.models.functions import TruncDay, TruncWeek
import json
from timetable.models import Event

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        tasks = tasks.filter(title__icontains=search_query) | tasks.filter(description__icontains=search_query)

    # Date range filter
    start_due = request.GET.get('start_due')
    end_due = request.GET.get('end_due')
    if start_due and end_due:
        tasks = tasks.filter(due_date__range=[start_due, end_due])

    # Get the current time
    now = timezone.now()

    # Check for tasks due within the next 24 hours
    soon_due_tasks = tasks.filter(due_date__range=[now, now + timedelta(days=1)], status='pending')

    # Filtering logic (if applied)
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    priority_filter = request.GET.get('priority')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    sort_by = request.GET.get('sort_by', 'due_date')
    tasks = tasks.order_by(sort_by)

    context = {
        'tasks': tasks,
        'soon_due_tasks': soon_due_tasks,
    }
    
    return render(request, 'todo/task_list.html', context)

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task created successfully!")
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'todo/task_form.html', {'form': form})

@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'todo/task_form.html', {'form': form})

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        # Delete the corresponding calendar event, if any
        if hasattr(task, 'event'):
            task.event.delete()  # Delete the linked event in the timetable

        task.delete()  # Delete the task itself
        messages.success(request, "Task deleted successfully!")
        return redirect('task_list')
    return render(request, 'todo/task_confirm_delete.html', {'task': task})

@login_required
def task_toggle_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if task.status == 'pending':
        task.status = 'completed'
        task.completed_at = timezone.now()  # Track when task is completed
        
        # Remove associated event when task is marked as completed
        if hasattr(task, 'event'):
            task.event.delete()  # Remove the event from the calendar

    else:
        task.status = 'pending'
        task.completed_at = None  # Reset completion date if toggled back
        # Optionally, you can re-create the event if task is toggled back to pending

    task.save()
    messages.success(request, f"Task '{task.title}' status updated!")
    return redirect('task_list')

@login_required
def task_completion_trends(request):
    tasks = Task.objects.filter(user=request.user, status='completed')

    # Count tasks completed on time and overdue
    on_time_tasks = tasks.filter(due_date__gte=F('completed_at')).count()
    overdue_tasks = tasks.filter(due_date__lt=F('completed_at')).count()

    context = {
        'on_time_tasks': on_time_tasks,
        'overdue_tasks': overdue_tasks,
    }

    return render(request, 'todo/task_completion_trends.html', context)

# Task History: Calendar or Timeline View
@login_required
def task_history(request):
    completed_tasks = Task.objects.filter(user=request.user, status='completed')

    # Format tasks as events for the calendar view
    events = []
    for task in completed_tasks:
        events.append({
            'title': task.title,
            'start': task.completed_at.isoformat(),
            'end': task.completed_at.isoformat(),
        })

    context = {
        'events': events,
        'tasks': completed_tasks,
    }

    return render(request, 'todo/task_history.html', context)

# Task Visual Reporting: Breakdown of Tasks Completed Per Day/Week
@login_required
def task_visual_reporting(request):
    completed_tasks = Task.objects.filter(user=request.user, status='completed')

    # Group by day or week
    tasks_per_day = completed_tasks.annotate(day=TruncDay('completed_at')).values('day').annotate(count=Count('id'))
    tasks_per_week = completed_tasks.annotate(week=TruncWeek('completed_at')).values('week').annotate(count=Count('id'))

    context = {
        'tasks_per_day': list(tasks_per_day),
        'tasks_per_week': list(tasks_per_week),
    }

    return render(request, 'todo/task_visual_reporting.html', context)

@require_POST
@login_required
def reorder_tasks(request):
    """Handles the reordering of tasks."""
    try:
        # Get the posted data (task IDs and their new order)
        task_order = json.loads(request.body)

        # Update the tasks' order in the database
        for order_data in task_order:
            task_id = order_data['id']
            task = Task.objects.get(id=task_id, user=request.user)
            task.order = order_data['order']
            task.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# New view to convert tasks into events
@login_required
def convert_task_to_event(request, task_id):
    """Convert a task into an event."""
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.to_event()  # Call the task's to_event method
        messages.success(request, "Task converted to event successfully!")
        return redirect('task_list')
    return render(request, 'todo/convert_task_to_event.html', {'task': task})
