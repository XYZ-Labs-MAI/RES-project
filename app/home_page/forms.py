from django import forms
from datetime import date
from authenticate.models import Users_History, Users


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Users_History
        fields = ['original_image']  # Поле для загрузки изображения

class UserUpdateForm(forms.ModelForm):
    # Форма для редактирования профиля на странице profile.
    class Meta:
        model = Users
        fields = ['username', 'email', ]