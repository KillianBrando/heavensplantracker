# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text=None  # Remove the default help text
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        help_text=None  # Remove the default help text
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        help_texts = {
            'username': None,  # Remove the help text for the username field
        }
        labels = {
            'username': 'Username',  # You can customize the labels if needed
        }
