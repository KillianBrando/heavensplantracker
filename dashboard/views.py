from django.shortcuts import render
from django.views.decorators.cache import cache_page  # Import the cache_page decorator
from django.db.models import Sum, Avg, F, Count
from django.contrib.auth.decorators import login_required
from expense.models import Expense, Income
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, TruncWeek
from todo.models import Task
from django.utils import timezone

@login_required
@cache_page(60 * 15)  # Cache the dashboard view for 15 minutes
def dashboard_view(request):
    today = datetime.today()
    start_of_month = today.replace(day=1)

    try:
        start_date = request.GET.get('start_date', start_of_month)
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    except (ValueError, TypeError):
        start_date = start_of_month
    
    try:
        end_date = request.GET.get('end_date', today)
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except (ValueError, TypeError):
        end_date = today

    # Get filter criteria from request
    start_date = request.GET.get('start_date', start_of_month)
    end_date = request.GET.get('end_date', today)

    # Optimize queries and fetch data, now filtered by the logged-in user
    expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date]).select_related('category')
    incomes = Income.objects.filter(user=request.user, date__range=[start_date, end_date]).select_related('source')

    total_spending = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_spending

    avg_spending_per_category = expenses.values('category').annotate(avg_amount=Avg('amount'))
    daily_expenses = expenses.annotate(day=TruncDay('date')).values('day').annotate(total=Sum('amount')).order_by('day')
    daily_income = incomes.annotate(day=TruncDay('date')).values('day').annotate(total=Sum('amount')).order_by('day')

    tasks = Task.objects.filter(user=request.user).prefetch_related('user')
    pending_tasks = tasks.filter(status='pending').count()
    completed_tasks = tasks.filter(status='completed').count()
    recent_tasks = tasks.order_by('-due_date')[:5]

    now = timezone.now()
    soon_due_tasks = tasks.filter(due_date__range=[now, now + timedelta(days=1)], status='pending')

    on_time_tasks = tasks.filter(status='completed', due_date__gte=F('completed_at')).count()
    overdue_tasks = tasks.filter(status='completed', due_date__lt=F('completed_at')).count()

    tasks_per_day = tasks.filter(status='completed').annotate(day=TruncDay('completed_at')).values('day').annotate(count=Count('id'))
    tasks_per_week = tasks.filter(status='completed').annotate(week=TruncWeek('completed_at')).values('week').annotate(count=Count('id'))

    spending_by_category = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    
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
    }

    return render(request, 'dashboard.html', context)