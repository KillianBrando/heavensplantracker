# weather/urls.py
from django.urls import path
from .views import weather_view, multi_city_dashboard, add_city, remove_city

app_name = 'weather'

urlpatterns = [
    path('', weather_view, name='weather'),
    path('dashboard/', multi_city_dashboard, name='multi_city_dashboard'),
    path('add_city/', add_city, name='add_city'),
    path('remove_city/<int:city_id>/', remove_city, name='remove_city'),  # corrected from <str:city_name> to <int:city_id>
]