from __future__ import absolute_import
from celery import Celery

app = Celery('articles')

app.conf.update(
                   CELERY_TASK_RESULT_EXPIRES = 3600,
                   )

