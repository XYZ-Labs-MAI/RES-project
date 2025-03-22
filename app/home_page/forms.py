from django import forms
from authenticate.models import Users_History

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Users_History
        fields = ['original_image']  # Поле для загрузки изображения