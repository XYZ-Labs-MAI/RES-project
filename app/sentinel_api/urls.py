from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import download_image

app_name = 'sentinel_api'

urlpatterns = [
    path('search/', views.search_view, name='search'),
    path('download/<str:filename>/', download_image, name='download_image'),
    path('settings/', views.settings_view, name ='settings' ),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)