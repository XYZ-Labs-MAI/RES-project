from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Users

class UserRegisterForm(UserCreationForm):

    class Meta:
        model = Users  # 🔗 Здесь связь с кастомной моделью Users
        fields = ['username',  'password1', 'password2']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', max_length=30, required=True)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    
    class Meta:
        model = Users
        fields = ['username', 'password']