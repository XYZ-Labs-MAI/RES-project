from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Хэширование пароля
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_register = models.DateTimeField(default=timezone.now)
    instance_id = models.CharField(max_length=150, blank=True, null = True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'  # Поле для входа в систему

    def __repr__(self):
        return f"<Users(id={self.id}, username='{self.username}', email='{self.email}')>"

    def __str__(self):
        return self.username

class Users_History(models.Model): # бд для истории запросов пользователя
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='history')
    original_image = models.ImageField(upload_to='original_images/')
    processed_image = models.ImageField(upload_to='processed_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return (f"<UserHistory(id={self.id}, user='{self.user.username}', "
                f"original_image='{self.original_image.url if self.original_image else 'N/A'}', "
                f"processed_image='{self.processed_image.url if self.processed_image else 'N/A'}', "
                f"created_at={self.created_at})>")


    def __str__(self):
        return f"История {self.user.username} в {self.created_at}"