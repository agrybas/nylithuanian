#encoding=utf-8
from __future__ import absolute_import
from smtplib import SMTPException

from events.models import Event
from articles.models import Article
from announcements.models import Announcement
from photos.models import Gallery
from classifieds.models import Classified
from newsletters.models import Newsletter
from users.models import SiteUser

from django.template.loader import get_template
from django.template import Context, RequestContext
from django.core.mail import EmailMultiAlternatives, get_connection
from django.shortcuts import render_to_response
from django.utils import timezone

import logging
from django.conf import settings



if settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)
    

if not settings.DEBUG:
    from .celery import app
    
    @app.task
    def send_newsletter(subject, from_address, recipient_list, message, html_message):
           
        conn = get_connection(backend='django.core.mail.backends.filebased.EmailBackend',)
        conn.open() # open single SMTP connection to use for mass email
        
        count = 0
        for to_address in recipient_list:
            try:
                logger.debug(u'Sending newsletter to {0}'.format(to_address))
                msg = EmailMultiAlternatives(subject, message, from_address, to=(to_address,), connection=conn)
                msg.attach_alternative(html_message, 'text/html')
                msg.send()
                count += 1
            except SMTPException:
                logger.error(u'An SMTP error occurred while sending email to {0}'.format(to_address))
            
        conn.close() # no more emails to send -- close connection
        logger.info(u'{0} newsletters sent successfully.'.format(count))