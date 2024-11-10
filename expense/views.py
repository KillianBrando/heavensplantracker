from .forms import ExpenseForm, BudgetForm, IncomeForm, IncomeFilterForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils.dateparse import parse_date
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Expense, Budget, Income
from django.contrib import messages
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expense/add_expense.html', {'form': form})

@login_required
def expense_list(request):
    today = timezone.now().date()

    # Get the 'start_date' and 'end_date' from the request, ensure they are strings or handle defaults
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Handle date parsing and defaults
    if start_date:
        start_date = parse_date(start_date)  # Parse the start date if it's provided as a string
    else:
        start_date = today.replace(day=1)  # Default to the first day of the current month

    if end_date:
        end_date = parse_date(end_date)  # Parse the end date if it's provided as a string
    else:
        end_date = today  # Default to today

    # Fetch expenses based on filters
    expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date])

    # Calculate total spent in each category
    categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Other']
    category_totals = {category: expenses.filter(category=category).aggregate(total=Sum('amount'))['total'] or 0 for category in categories}

    # Calculate daily expenses (spending over time)
    daily_expenses = expenses.annotate(day=TruncDay('date')).values('day').annotate(total=Sum('amount')).order_by('day')

    # Calculate total expenses
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Render the filtered expense list and summary
    return render(request, 'expense/expense_list.html', {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'start_date': start_date,
        'end_date': end_date,
        'category_totals': category_totals,
        'daily_expenses': daily_expenses,
    })

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expense/edit_expense.html', {'form': form, 'expense': expense})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expense/confirm_delete.html', {'expense': expense})

@login_required
def budget_settings(request):
    budgets = Budget.objects.filter(user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('budget_settings')
    else:
        form = BudgetForm()

    context = {'budgets': budgets, 'form': form}
    return render(request, 'expense/budget_settings.html', context)

@csrf_exempt
def sync_expenses(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        synced_expenses = data.get('expenses', [])
        for expense in synced_expenses:
            existing_expense = Expense.objects.filter(
                user=request.user,
                date=datetime.strptime(expense['date'], '%Y-%m-%d'),
                amount=expense['amount'],
                category=expense['category'],
                description=expense['description']
            ).first()
            if not existing_expense:
                new_expense = Expense(
                    user=request.user,
                    date=datetime.strptime(expense['date'], '%Y-%m-%d'),
                    amount=expense['amount'],
                    category=expense['category'],
                    description=expense['description']
                )
                new_expense.save()
        return JsonResponse({"status": "success"})

    return JsonResponse({"error": "Invalid method"}, status=400)

@login_required
def edit_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('budget_settings')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'expense/edit_budget.html', {'form': form})

@login_required
def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        return redirect('budget_settings')
    return render(request, 'expense/confirm_delete_budget.html', {'budget': budget})

@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('income_list')
    else:
        form = IncomeForm()
    return render(request, 'expense/add_income.html', {'form': form})

@login_required
def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'expense/edit_income.html', {'form': form, 'income': income})

@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        income.delete()
        return redirect('income_list')
    return render(request, 'expense/confirm_delete_income.html', {'income': income})

@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user)
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0

    if request.method == 'GET':
        filter_form = IncomeFilterForm(request.GET)
        if filter_form.is_valid():
            if filter_form.cleaned_data['start_date']:
                start_date = filter_form.cleaned_data['start_date']
                incomes = incomes.filter(date__gte=start_date)
            if filter_form.cleaned_data['end_date']:
                end_date = filter_form.cleaned_data['end_date']
                incomes = incomes.filter(date__lte=end_date)
            if filter_form.cleaned_data['source']:
                incomes = incomes.filter(source__icontains=filter_form.cleaned_data['source'])
            total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0

    else:
        filter_form = IncomeFilterForm()

    income_trends = incomes.values('date').annotate(total_income=Sum('amount')).order_by('date')
    income_by_source = incomes.values('source').annotate(total_income=Sum('amount')).order_by('-total_income')

    daily_income = incomes.values('date').annotate(total=Sum('amount')).order_by('-date')
    weekly_income = incomes.annotate(week=TruncWeek('date')).values('week').annotate(total=Sum('amount')).order_by('-week')
    monthly_income = incomes.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('-month')

    return render(request, 'expense/income_list.html', {
        'incomes': incomes,
        'total_income': total_income,
        'filter_form': filter_form,
        'income_trends': income_trends,
        'income_by_source': income_by_source,
        'daily_income': daily_income,
        'weekly_income': weekly_income,
        'monthly_income': monthly_income
    })
