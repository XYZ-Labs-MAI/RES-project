import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "XYZ_labs.settings")
app = Celery("XYZ_labs")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()