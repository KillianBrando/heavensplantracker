from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),  # Task listing view
    path('create/', views.task_create, name='task_create'),  # Task creation view
    path('edit/<int:task_id>/', views.task_edit, name='task_edit'),  # Task editing view
    path('delete/<int:task_id>/', views.task_delete, name='task_delete'),  # Task deletion view
    path('toggle_complete/<int:task_id>/', views.task_toggle_complete, name='task_toggle_complete'),  # Toggle task completion
    path('reorder_tasks/', views.reorder_tasks, name='reorder_tasks'),  # Reorder tasks via drag-and-drop
    path('completion_trends/', views.task_completion_trends, name='task_completion_trends'),  # Task completion trends (analytics)
    path('history/', views.task_history, name='task_history'),  # Task history (calendar or timeline view)
    path('visual_reporting/', views.task_visual_reporting, name='task_visual_reporting'),  # Task visual reporting (breakdown of completed tasks)
    path('convert_to_event/<int:task_id>/', views.convert_task_to_event, name='convert_task_to_event'),  # Convert task to event
]
