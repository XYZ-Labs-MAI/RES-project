from django.urls import path
from .api import api

urlpatterns = [
    path('', api.process_image_api),
]