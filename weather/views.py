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

# Multi-City Weather Dashboard View
@login_required
def multi_city_dashboard(request):
    user = request.user
    api_key = settings.OPENWEATHER_API_KEY
    unit = request.session.get('unit', 'metric')
    units_label = '°C' if unit == 'metric' else '°F'
    
    cities = user.cities.all()
    weather_data_list = []
    
    for city in cities:
        cache_key = hashlib.md5(f"{city.city_name}-{unit}".encode()).hexdigest()
        cached_data = cache.get(cache_key)
        
        if cached_data:
            weather_data = cached_data['weather_data']
        else:
            try:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city.city_name}&appid={api_key}&units={unit}"
                response = requests.get(url)
                response.raise_for_status()
                weather_data = response.json()
                cache.set(cache_key, {'weather_data': weather_data}, timeout=900)
            except requests.exceptions.RequestException:
                messages.error(request, f"Unable to retrieve weather data for {city.city_name}.")
                weather_data = None
        
        if weather_data:
            weather_data_list.append({
                'city_id': city.id,  # Include city_id for the remove link
                'city': city.city_name,
                'temperature': weather_data['main']['temp'],
                'description': weather_data['weather'][0]['main'],
                'units_label': units_label,
                'icon': weather_data['weather'][0]['icon']
            })

    return render(request, 'weather/multi_city_dashboard.html', {'weather_data_list': weather_data_list})

# Add City to Multi-City Dashboard
@login_required
def add_city(request):
    if request.method == 'POST':
        city_name = request.POST.get('city_name')
        if city_name:
            existing_city = UserCity.objects.filter(user=request.user, city_name=city_name).first()
            if not existing_city:
                UserCity.objects.create(user=request.user, city_name=city_name)
                messages.success(request, f"{city_name} added to your dashboard.")
            else:
                messages.info(request, f"{city_name} is already in your dashboard.")
    return redirect(reverse('weather:multi_city_dashboard'))

# Remove City from Multi-City Dashboard
@login_required
def remove_city(request, city_id):
    city = UserCity.objects.filter(id=city_id, user=request.user).first()
    if city:
        city.delete()
        messages.success(request, f"{city.city_name} removed from your dashboard.")
    else:
        messages.error(request, "City not found.")
    return redirect(reverse('weather:multi_city_dashboard'))
