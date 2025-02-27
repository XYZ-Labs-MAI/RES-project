from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Users

class UserRegisterForm(UserCreationForm): # форма для регистрации

    class Meta:
        model = Users  # Здесь связь с кастомной моделью Users
        fields = ['username',  'password1', 'password2']

    def __repr__(self):
        return f"<UserRegisterForm(username={self.cleaned_data.get('username', 'N/A')}, password1=****, password2=****)>"


class UserLoginForm(AuthenticationForm): # форма логина
    username = forms.CharField(label='Имя пользователя', max_length=30, required=True)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def __repr__(self):
        return f"<UserLoginForm(username={self.cleaned_data.get('username', 'N/A')}, password=****)>"
    
    class Meta:
        model = Users
        fields = ['username', 'password']