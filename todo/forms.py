from django import forms
from .models import Task
from django.utils import timezone

class TaskForm(forms.ModelForm):
    add_to_calendar = forms.BooleanField(required=False, label='Add to Calendar')

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date', 'status', 'recurring', 'add_to_calendar']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control datepicker'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'recurring': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due_date

    def save(self, commit=True):
        task = super().save(commit=False)
        if commit:
            task.save()
            # If 'add to calendar' is checked, create an event
            if self.cleaned_data.get('add_to_calendar'):
                task.to_event()
        return task
