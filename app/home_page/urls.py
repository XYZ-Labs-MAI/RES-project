from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_page_show),
    path('profile/', views.profile_view, name='profile'),  
]