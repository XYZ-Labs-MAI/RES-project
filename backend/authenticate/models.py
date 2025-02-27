from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Users(AbstractUser):
    def __repr__(self):
        return f"<Users(id={self.id}, username='{self.username}', email='{self.email}')>"

class UserHistory(models.Model): # бд для истории запросов пользователя
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='history')
    original_image = models.ImageField(upload_to='original_images/')
    processed_image = models.ImageField(upload_to='processed_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return (f"<UserHistory(id={self.id}, user='{self.user.username}', "
                f"original_image='{self.original_image.url if self.original_image else 'N/A'}', "
                f"processed_image='{self.processed_image.url if self.processed_image else 'N/A'}', "
                f"created_at={self.created_at})>")


    def __str__(self):
        return f"История {self.user.username} в {self.created_at}"