from django import forms
from datetime import date
from authenticate.models import Users


class SentinelSearchForm(forms.Form):
    CRS_CHOICES = [
        ('EPSG:4326', 'WGS 84 (EPSG:4326) - Широта/Долгота'),
        ('EPSG:3857', 'Web Mercator (EPSG:3857) - для карт'),

    ]
    
    # Границы области
    upper_left_lon = forms.FloatField(
        label="Верхний левый угол (долгота/X)",
        widget=forms.NumberInput(attrs={
            'step': '0.0001',
            'class': 'form-control',
            'placeholder': '-180 до 180'
        })
    )
    
    upper_left_lat = forms.FloatField(
        label="Верхний левый угол (широта/Y)",
        widget=forms.NumberInput(attrs={
            'step': '0.0001',
            'class': 'form-control',
            'placeholder': '-90 до 90'
        })
    )
    
    lower_right_lon = forms.FloatField(
        label="Нижний правый угол (долгота/X)",
        widget=forms.NumberInput(attrs={
            'step': '0.0001',
            'class': 'form-control',
            'placeholder': '-180 до 180'
        })
    )
    
    lower_right_lat = forms.FloatField(
        label="Нижний правый угол (широта/Y)",
        widget=forms.NumberInput(attrs={
            'step': '0.0001',
            'class': 'form-control',
            'placeholder': '-90 до 90'
        })
    )
    
    # Система координат
    srs = forms.ChoiceField(
        label="Система координат",
        choices=CRS_CHOICES,
        initial='EPSG:4326',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Параметры облачности
    max_cloud_cover = forms.IntegerField(
        label="Максимальная облачность (%)",
        min_value=0,
        max_value=100,
        initial=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    # Диапазон дат
    start_date = forms.DateField(
        label="Начальная дата",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        initial=date.today
    )
    
    end_date = forms.DateField(
        label="Конечная дата",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        initial=date.today
    )
    
    # Количество изображений
    max_images = forms.IntegerField(
        label="Количество изображений (1-10)",
        min_value=1,
        max_value=10,
        initial=3,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Проверка координат
        ul_lon = cleaned_data.get('upper_left_lon')
        ul_lat = cleaned_data.get('upper_left_lat')
        lr_lon = cleaned_data.get('lower_right_lon')
        lr_lat = cleaned_data.get('lower_right_lat')

        # Проверка дат
        if cleaned_data.get('start_date') and cleaned_data.get('end_date'):
            if cleaned_data['start_date'] > cleaned_data['end_date']:
                self.add_error('end_date', 'Должна быть после начальной даты')
        
        return cleaned_data
    
    def get_bbox(self):
        """Возвращает bbox в формате [min_lon, min_lat, max_lon, max_lat]"""
        if not self.is_valid():
            raise ValueError("Form data is invalid")
        
        return {
            'bbox': [
                self.cleaned_data['upper_left_lon'],
                self.cleaned_data['lower_right_lat'],
                self.cleaned_data['lower_right_lon'],
                self.cleaned_data['upper_left_lat']
            ],
            'srs': self.cleaned_data['srs']
        }


class SentinelInstanceForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['instance_id']
        labels = {
            'sentinel_instance_id': 'Ваш Sentinel Hub Instance ID'
        }