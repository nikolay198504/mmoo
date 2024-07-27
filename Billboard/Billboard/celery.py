import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Billboard.settings')

app = Celery('Billboard')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.timezone = 'UTC'
