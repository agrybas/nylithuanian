from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nylithuanian.settings')
    
app = Celery('nylithuanian')

app.config_from_object('nylithuanian.settings')
app.autodiscover_tasks(settings.INSTALLED_APPS)
