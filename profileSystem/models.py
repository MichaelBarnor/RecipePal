from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    allergies = models.TextField(blank=True, null=True)
    favorite_foods = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
