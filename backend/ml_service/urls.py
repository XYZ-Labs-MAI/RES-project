from django.urls import path
from .api_no_mlt import api

urlpatterns = [
    path('', api.urls),
]