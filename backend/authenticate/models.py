from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Users(AbstractUser):
    pass

class UserHistory(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='history')
    original_image = models.ImageField(upload_to='original_images/')
    processed_image = models.ImageField(upload_to='processed_images/')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"История {self.user.username} в {self.created_at}"