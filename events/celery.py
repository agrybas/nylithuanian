from __future__ import absolute_import
from celery import Celery

celery = Celery('events.celery', broker='amqp://rabbit_user:234wer234@localhost:5672/macvhost', backend='amqp://', include=['events.tasks'])

celery.conf.update(
                   CELERY_TASK_RESULT_EXPIRES = 3600,
                   )

if __name__ == '__main__':
    celery.start()
    
