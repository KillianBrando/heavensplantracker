# expense_tracker/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), 
    path('expenses/', include('expense.urls')),
    path('todo/', include('todo.urls')),
    path('timetable/', include('timetable.urls')),
    path('', include('dashboard.urls')),
    path('weather/', include('weather.urls')),
]
