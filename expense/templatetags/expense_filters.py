# expense/templatetags/expense_filters.py
from django import template

register = template.Library()

@register.filter(name='mmk')
def mmk_format(value):
    """Custom filter to format currency in MMK"""
    try:
        value = float(value)
        return "MMK {:,.2f}".format(value)
    except (ValueError, TypeError):
        return value
