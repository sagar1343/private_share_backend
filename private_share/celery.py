import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "private_share.settings.dev")

app = Celery("private_share")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
