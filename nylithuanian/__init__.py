from __future__ import absolute_import
from django.conf import settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nylithuanian.settings")

if not settings.DEBUG:
    # This will make sure the app is always imported when
    # Django starts so that shared_task will use this app.
    from .celery import app as celery_app