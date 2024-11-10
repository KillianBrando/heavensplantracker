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
from django.core.cache import cache

def fetch_weather_info(city="Your_City"):
    weather_info = {}
    weather_alert = ""

    # Cache weather data for 10 minutes to avoid excessive calls
    cache_key = f"weather_data_{city}"
    cached_weather = cache.get(cache_key)

    if cached_weather:
        print("Using cached weather data")
        return cached_weather["weather_info"], cached_weather["weather_alert"]

    try:
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

        # Set alert based on condition
        condition = weather_info['condition'].lower()
        if 'rain' in condition:
            weather_alert = "It might rain soon. Remember to take an umbrella!"
        elif 'snow' in condition:
            weather_alert = "Snow is expected. Dress warmly!"
        elif 'storm' in condition or 'thunderstorm' in condition:
            weather_alert = "A storm is coming. Avoid travel if possible."
        elif 'clear' in condition:
            weather_alert = "Clear skies ahead. Enjoy your day!"

        # Cache the data to reduce API calls
        cache.set(cache_key, {"weather_info": weather_info, "weather_alert": weather_alert}, timeout=600)

    except requests.RequestException as e:
        weather_alert = "Weather data is currently unavailable."
        print(f"Error fetching weather data: {e}")  # Log the actual error message

    return weather_info, weather_alert

@login_required
@cache_page(60 * 15)  # Cache for 15 minutes
def dashboard_view(request):
    today = datetime.today()
    start_of_month = today.replace(day=1)

    # Parse start and end dates from request, with defaults
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else start_of_month
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else today
    except ValueError:
        start_date, end_date = start_of_month, today

    # Retrieve financial data for date range
    expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date]).select_related('category')
    incomes = Income.objects.filter(user=request.user, date__range=[start_date, end_date]).select_related('source')

    total_spending = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_spending

    # Analytics for expenses and tasks
    avg_spending_per_category = expenses.values('category').annotate(avg_amount=Avg('amount'))
    daily_expenses = expenses.annotate(day=TruncDay('date')).values('day').annotate(total=Sum('amount')).order_by('day')
    daily_income = incomes.annotate(day=TruncDay('date')).values('day').annotate(total=Sum('amount')).order_by('day')

    tasks = Task.objects.filter(user=request.user)
    pending_tasks = tasks.filter(status='pending').count()
    completed_tasks = tasks.filter(status='completed').count()
    recent_tasks = tasks.order_by('-due_date')[:5]
    soon_due_tasks = tasks.filter(due_date__range=[timezone.now(), timezone.now() + timedelta(days=1)], status='pending')
    on_time_tasks = tasks.filter(status='completed', due_date__gte=F('completed_at')).count()
    overdue_tasks = tasks.filter(status='completed', due_date__lt=F('completed_at')).count()
    tasks_per_day = tasks.filter(status='completed').annotate(day=TruncDay('completed_at')).values('day').annotate(count=Count('id'))
    tasks_per_week = tasks.filter(status='completed').annotate(week=TruncWeek('completed_at')).values('week').annotate(count=Count('id'))

    spending_by_category = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')

    # Fetch weather information and alert
    weather_info, weather_alert = fetch_weather_info()

    # Compile context data
    context = {
        'total_spending': total_spending,
        'total_income': total_income,
        'balance': balance,
        'avg_spending_per_category': avg_spending_per_category,
        'daily_expenses': daily_expenses,
        'daily_income': daily_income,
        'start_date': start_date,
        'end_date': end_date,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'recent_tasks': recent_tasks,
        'soon_due_tasks': soon_due_tasks,
        'on_time_tasks': on_time_tasks,
        'overdue_tasks': overdue_tasks,
        'tasks_per_day': tasks_per_day,
        'tasks_per_week': tasks_per_week,
        'spending_by_category': spending_by_category,
        'weather_alert': weather_alert,
        'weather_info': weather_info
    }

    return render(request, 'dashboard.html', context)
