import requests
import hashlib
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from .forms import CityForm
from .models import UserCity

# Get the API key securely from settings
API_KEY = settings.OPENWEATHER_API_KEY

# Single City Weather View
def weather_view(request):
    city = request.GET.get('city', 'Yangon')
    unit = request.session.get('unit', 'metric')
    units_label = '°C' if unit == 'metric' else '°F'
    
    if 'unit' in request.GET:
        unit = request.GET['unit']
        request.session['unit'] = unit
        units_label = '°C' if unit == 'metric' else '°F'
    
    cache_key = hashlib.md5(f"{city}-{unit}".encode()).hexdigest()
    cached_data = cache.get(cache_key)
    
    # Initialize geo_data and forecast_data with default values
    geo_data, forecast_data = {}, []

    if cached_data:
        geo_data = cached_data.get('weather_data', {})
        forecast_data = cached_data.get('forecast_data', [])
    else:
        try:
            geo_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"
            geo_response = requests.get(geo_url)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            lat = geo_data['coord']['lat']
            lon = geo_data['coord']['lon']
            
            forecast_url = f"http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={API_KEY}&units={unit}"
            forecast_response = requests.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json().get('daily', [])
            
            cache.set(cache_key, {'weather_data': geo_data, 'forecast_data': forecast_data}, timeout=900)
        except requests.exceptions.RequestException:
            messages.error(request, "Unable to retrieve weather data at this time.")

    form = CityForm(initial={'city': city})
    return render(request, 'weather/weather.html', {
        'weather_data': geo_data,
        'forecast_data': forecast_data,
        'form': form,
        'city': city,
        'units_label': units_label
    })

