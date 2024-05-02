import random, os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.html import mark_safe
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone 
from .utils import get_upload_to
import uuid
from datetime import timedelta

class UserProfile(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True)
    displayname = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    avatar = models.ImageField(upload_to=get_upload_to, null=True, blank=True)
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)], null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    match_preferences = models.OneToOneField('MatchPreferences', on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    location = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    level = models.PositiveIntegerField(default=1)
    interaction_history = models.ManyToManyField('Interaction', blank=True)
    is_42student = models.BooleanField(default=False)
    kind = models.CharField(max_length=30, blank=True)
    campus = models.CharField(max_length=50, blank=True)

    def __str__(self) -> str:
        return f"{self.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    @property
    def thumbnail(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.avatar.url))

class Interaction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    superlike = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} - {self.timestamp}'

class MatchPreferences(models.Model):
    user = models.OneToOneField('UserProfile', on_delete=models.CASCADE, related_name='match_preferences')
    preferred_gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('any', 'Any')], default='any')
    preferred_age_min = models.PositiveIntegerField(default=18)
    preferred_age_max = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f'Match Preferences for {self.user.username}'