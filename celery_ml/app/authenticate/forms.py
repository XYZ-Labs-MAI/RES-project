from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Users

class UserRegisterForm(UserCreationForm): # форма для регистрации

    class Meta:
        model = Users  # Здесь связь с кастомной моделью Users
        fields = ['username', 'email',  'password1', 'password2']

    def __repr__(self):
        return f"<UserRegisterForm(username={self.cleaned_data.get('username', 'N/A')}, password1=****, password2=****)>"


class UserLoginForm(AuthenticationForm):  # Форма для логина
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'  # Изменяем лейбл
        self.fields['password'].label = 'Пароль'  # Изменяем лейбл

    def __repr__(self):
        return f"<UserLoginForm(username={self.cleaned_data.get('username', 'N/A')}, password=****)>"