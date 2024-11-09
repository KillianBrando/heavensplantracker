from django import forms
from .models import Expense, Budget, Income
from django.utils import timezone

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'amount', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'description': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'maxlength': 255}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number.")
        return amount

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date > timezone.now().date():
            raise forms.ValidationError("Date cannot be in the future.")
        return date

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'limit']
        widgets = {
            'category': forms.Select(choices=[
                ('Food', 'Food'), 
                ('Transport', 'Transport'), 
                ('Utilities', 'Utilities'), 
                ('Entertainment', 'Entertainment'), 
                ('Other', 'Other')
            ], attrs={'class': 'form-select form-select-lg'}),
            'limit': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
        }

    def clean_limit(self):
        limit = self.cleaned_data.get('limit')
        if limit <= 0:
            raise forms.ValidationError("Budget limit must be a positive number.")
        return limit

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['date', 'amount', 'source', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
            'source': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-lg', 'rows': 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number.")
        return amount

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date > timezone.now().date():
            raise forms.ValidationError("Date cannot be in the future.")
        return date

class IncomeFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    source = forms.CharField(max_length=100, required=False)
