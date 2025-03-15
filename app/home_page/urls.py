from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page_show, name="home_page"),
    path('profile/', views.profile, name='profile'),
    path('history/', views.HistoryListView.as_view(), name = 'history'),
    path('main/', views.main_page, name = 'main_page'),
]
