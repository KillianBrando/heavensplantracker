# weather/models.py
from django.db import models
from django.conf import settings

class UserCity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cities')
    city_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city_name} for {self.user.username}"
