from django.urls import path
from .views import upload_image, get_detection_result, detection_view

urlpatterns = [
    path('upload/', upload_image, name='upload_detect'),
    path('result/<str:task_id>/', get_detection_result, name='detection_result'),
    path('', detection_view, name='detection_view'),
]