# urls.py
from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('daily/', views.daily_view, name='daily_view'),
    path('create/', views.create_event, name='create_event'),
    path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('api/events/', views.api_get_events, name='api_get_events'),
]