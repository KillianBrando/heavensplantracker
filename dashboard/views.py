import requests
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.db.models import Sum, Avg, F, Count
from django.contrib.auth.decorators import login_required
from expense.models import Expense, Income
from todo.models import Task
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, TruncWeek
from django.conf import settings

@login_required
@cache_page(60 * 15)  # Cache the dashboard view for 15 minutes
def dashboard_view(request):
    today = datetime.today()
    start_of_month = today.replace(day=1)

    # Date filtering for analytics
    start_date = request.GET.get('start_date', start_of_month)
    end_date = request.GET.get('end_date', today)

    # Financial data retrieval
    expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date]).select_related('category')
    incomes = Income.objects.filter(user=request.user, date__range=[start_date, end_date]).select_related('source')

    total_spending = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0

    # Task and analytics data
    tasks = Task.objects.filter(user=request.user)
    pending_tasks = tasks.filter(status='pending').count()
    completed_tasks = tasks.filter(status='completed').count()
    recent_tasks = tasks.order_by('-due_date')[:5]
    soon_due_tasks = tasks.filter(due_date__range=[timezone.now(), timezone.now() + timedelta(days=1)], status='pending')

    # Weather-based alerts and information
    weather_alert = ""
    weather_info = {}
    try:
        city = "Your_City"  # Replace with actual city or dynamically get from user profile
        api_key = settings.OPENWEATHER_API_KEY
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(weather_url)
        response.raise_for_status()
        weather_data = response.json()

        # Extract relevant weather information
        weather_info = {
            "temperature": weather_data['main']['temp'],
            "condition": weather_data['weather'][0]['main'],
            "icon_url": f"http://openweathermap.org/img/wn/{weather_data['weather'][0]['icon']}@2x.png"
        }

        # Set alerts based on conditions
        if 'rain' in weather_info['condition'].lower():
            weather_alert = "It looks like it might rain soon. Remember to take an umbrella when you go out!"
        elif 'snow' in weather_info['condition'].lower():
            weather_alert = "Snow is expected soon. Dress warmly and drive safely!"
        elif 'storm' in weather_info['condition'].lower() or 'thunderstorm' in weather_info['condition'].lower():
            weather_alert = "A storm is on the way. Stay indoors if possible."
        elif 'clear' in weather_info['condition'].lower():
            weather_alert = "Clear skies ahead. Enjoy your day!"
    except requests.RequestException:
        weather_alert = "Weather data is currently unavailable."

    context = {
        'total_spending': total_spending,
        'total_income': total_income,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'recent_tasks': recent_tasks,
        'soon_due_tasks': soon_due_tasks,
        'weather_alert': weather_alert,  # Weather alert message
        'weather_info': weather_info  # Weather information for the dashboard
    }

    return render(request, 'dashboard.html', context)
