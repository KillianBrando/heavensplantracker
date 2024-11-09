# expense/urls.py
from django.urls import path
from . import views
urlpatterns = [
    path('add/', views.add_expense, name='add_expense'),  # Add Expense URL
    path('', views.expense_list, name='expense_list'),    # Expense List URL
    path('<int:pk>/edit/', views.edit_expense, name='edit_expense'),  # Edit Expense URL
    path('<int:pk>/delete/', views.delete_expense, name='delete_expense'),  # Delete Expense URL
    path('budget/', views.budget_settings, name='budget_settings'),  # Budget Settings URL
    path('sync/', views.sync_expenses, name='sync_expenses'),
    path('budget/edit/<int:pk>/', views.edit_budget, name='edit_budget'),
    path('budget/delete/<int:pk>/', views.delete_budget, name='delete_budget'),
    path('income/add/', views.add_income, name='add_income'),
    path('income/list/', views.income_list, name='income_list'),
    path('income/edit/<int:pk>/', views.edit_income, name='edit_income'), 
    path('income/delete/<int:pk>/', views.delete_income, name='delete_income'),
]
