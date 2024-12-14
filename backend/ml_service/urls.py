from django.urls import path
from . import api

urlpatterns = [
    path('', api.process_image_api),
]