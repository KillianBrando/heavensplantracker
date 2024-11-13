# File: todo/templatetags/task_tags.py
from django import template

register = template.Library()

@register.filter
def task_priority_color(priority):
    colors = {
        'high': 'bg-danger',
        'medium': 'bg-warning',
        'low': 'bg-secondary',
    }
    return colors.get(priority, 'bg-secondary')

@register.filter
def task_status_color(status):
    colors = {
        'completed': 'bg-success',
        'pending': 'bg-primary',
    }
    return colors.get(status, 'bg-primary')
