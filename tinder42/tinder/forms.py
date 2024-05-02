from django.core.mail import EmailMultiAlternatives
from django import forms
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import authenticate
from .models import Interaction, MatchPreferences

class MatchPreferencesForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    preffered_gender = forms.ChoiceField(choices=GENDER_CHOICES)
    preferred_age_min = forms.IntegerField(min_value=18, max_value=100)
    preferred_age_max = forms.IntegerField(min_value=18, max_value=100)