from __future__ import absolute_import
from celery import Celery
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nylithuanian.settings')

app = Celery('events')

app.config_from_object('nylithuanian.settings')
# app.autodiscover_tasks(['events'])