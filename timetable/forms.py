from django import forms
from .models import Event
from django.utils import timezone
from django.core.exceptions import ValidationError

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_time', 'end_time', 'recurring_option']
        
        # Enhanced widgets with applied classes
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-lg', 'rows': 4}),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control form-control-lg datetimepicker',
                'placeholder': 'Select start date and time'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control form-control-lg datetimepicker',
                'placeholder': 'Select end date and time'
            }),
            'recurring_option': forms.Select(attrs={'class': 'form-select form-select-lg'}),
        }

    # Validation to ensure start_time is in the future
    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if start_time and start_time < timezone.now():
            raise ValidationError("Start time must be in the future.")
        return start_time

    # Validation to ensure end_time is after start_time
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time and start_time >= end_time:
            raise ValidationError("End time must be after the start time.")
        return cleaned_data
