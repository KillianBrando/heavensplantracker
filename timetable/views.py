from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event
from .forms import EventForm
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse
from django.utils.timezone import localtime
from todo.models import Task
from django.views.decorators.cache import cache_page

@login_required
def event_list(request):
    """Display all events, including recurring ones."""
    now = timezone.now()

    events = Event.objects.filter(user=request.user).order_by('start_time')

    all_events = []
    for event in events:
        if event.recurring_option != 'none':
            occurrences = event.get_next_occurrences(from_date=now, num_occurrences=1)
            if occurrences:
                first_occurrence = occurrences[0]
                all_events.append({
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'start_time': first_occurrence,
                    'end_time': first_occurrence + (event.end_time - event.start_time),
                    'recurring_option': event.get_recurring_option_display(),
                })
        else:
            all_events.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'recurring_option': None,
            })

    return render(request, 'timetable/event_list.html', {'events': all_events, 'now': now})

@login_required
def create_event(request):
    """Create a new event."""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('timetable:event_list')
    else:
        form = EventForm()

    return render(request, 'timetable/create_event.html', {'form': form})

@login_required
def daily_view(request):
    """Display events for the current day, including handling recurring events."""
    now = timezone.now().date()
    events = Event.objects.filter(user=request.user, start_time__date=now)

    recurring_events = []
    all_events = []

    for event in events:
        if event.recurring_option != 'none':
            occurrences = event.get_next_occurrences(from_date=timezone.now(), num_occurrences=1)
            if occurrences and occurrences[0].date() == now:
                next_occurrence = occurrences[0]
                recurring_events.append({
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'start_time': next_occurrence,
                    'end_time': next_occurrence + (event.end_time - event.start_time),
                    'recurring_option': event.get_recurring_option_display(),
                    'is_current': next_occurrence <= timezone.now() <= (next_occurrence + timedelta(hours=1))
                })
        else:
            all_events.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'recurring_option': None,
            })

    all_events += recurring_events

    return render(request, 'timetable/daily_view.html', {'events': all_events, 'now': timezone.now()})

@login_required
def edit_event(request, event_id):
    """Edit an existing event."""
    event = get_object_or_404(Event, id=event_id, user=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('timetable:event_list')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'timetable/edit_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    """Delete an event."""
    event = get_object_or_404(Event, id=event_id, user=request.user)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('timetable:event_list')
    
    return render(request, 'timetable/delete_event.html', {'event': event})

@login_required
def api_get_events(request):
    """Return events in JSON format for FullCalendar."""
    events = Event.objects.filter(user=request.user)
    all_events = []

    for event in events:
        if event.recurring_option != 'none':
            occurrences = event.get_next_occurrences(from_date=timezone.now(), num_occurrences=5)
            for occurrence in occurrences:
                all_events.append({
                    'id': event.id,
                    'title': event.title,
                    'start': localtime(occurrence).isoformat(),
                    'end': localtime(occurrence + (event.end_time - event.start_time)).isoformat(),
                    'is_task': event.is_task
                })
        else:
            all_events.append({
                'id': event.id,
                'title': event.title,
                'start': localtime(event.start_time).isoformat(),
                'end': localtime(event.end_time).isoformat(),
                'is_task': event.is_task
            })

    tasks = Task.objects.filter(user=request.user, due_date__isnull=False, event__isnull=True)
    for task in tasks:
        task_due_datetime = timezone.make_aware(datetime.combine(task.due_date, datetime.min.time()))
        all_events.append({
            'id': task.id,
            'title': task.title,
            'start': localtime(task_due_datetime).isoformat(),
            'end': localtime(task_due_datetime + timedelta(hours=1)).isoformat(),
            'is_task': True
        })

    return JsonResponse(all_events, safe=False)

@cache_page(60 * 15)  # Cache the calendar view for 15 minutes
@login_required
def calendar_view(request):
    events = Event.objects.filter(user=request.user).select_related('user')
    task_events = Task.objects.filter(user=request.user, due_date__isnull=False).prefetch_related('user')

    all_events = []

    for event in events:
        all_events.append({
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'description': event.description,
            'is_task': False
        })

    for task in task_events:
        all_events.append({
            'title': task.title,
            'start': task.due_date.isoformat(),
            'end': (task.due_date + timedelta(hours=1)).isoformat(),
            'description': task.description,
            'is_task': True
        })

    context = {'events': all_events}
    return render(request, 'timetable/calendar_view.html', context)
