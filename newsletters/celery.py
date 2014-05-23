from __future__ import absolute_import
from celery import Celery
from django.conf import settings
import os

if not settings.DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nylithuanian.settings')
    
    
    app = Celery('newsletters')
    
    app.config_from_object('django.conf:settings')
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)