#encoding=utf-8
from events.celery import celery
from nylithuanian import settings
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.template import Context

@celery.task
def send_reminder(event, recipient_email):
    plainText = get_template('emails/reminder.txt')
    htmlText = get_template('emails/reminder.html')
    to = [recipient_email,]
    subject = 'Priminimas apie renginį'
    c = Context({
                     'event' : event,
                     })
    
    msg = EmailMultiAlternatives(subject, plainText.render(c), settings.SERVER_EMAIL, to)
    msg.attach_alternative(htmlText.render(c), 'text/html')
    msg.send()
