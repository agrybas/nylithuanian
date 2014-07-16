#encoding=utf-8
from smtplib import SMTPException
from math import ceil, floor
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils import timezone
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.core.mail import EmailMultiAlternatives, get_connection
from django.shortcuts import render_to_response
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q

from events.models import Event
from articles.models import Article
from photos.models import Gallery
from users.models import SiteUser
from classifieds.models import Classified
from announcements.models import Announcement

from .models import Newsletter
from .forms import AddNewsletterForm
from tasks import *

import logging
import random


if settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)

class NewsletterListView(ListView):
    model = Newsletter
    paginate_by = 10
    

class NewsletterDetailView(DetailView):
    model = Newsletter
    #template_name = 'emails/newsletter.html'
    
    def get_context_data(self, **kwargs):
        kwargs['event_list'] = Event.public.filter(
                                   Q(end_date__isnull = False) & Q(end_date__gt = timezone.now()) |
                                   Q(start_date__gt = timezone.now())
                                   )
        kwargs['announcement_list'] = Announcement.public.order_by('-create_date')[:3]
        kwargs['article_list'] = Article.public.order_by('-create_date')[:3]
        kwargs['gallery_list'] = Gallery.objects.filter(is_public=True)[:5]
        kwargs['classified_list'] = Classified.public.all()[:5]
        kwargs['newsletter'] = Newsletter.objects.get(id=self.kwargs['pk'])
        return super(NewsletterDetailView, self).get_context_data(**kwargs)
     
class NewsletterUpdateView(UpdateView):
    model = Newsletter
    form_class = AddNewsletterForm
    success_url = '../'
    template_name = 'newsletters/newsletter_edit.html'
    
#     @staff_member_required
#     def dispatch(self, *args, **kwargs):
#         return super(NewsletterUpdateView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        kwargs['form'] = AddNewsletterForm(instance=Newsletter.objects.get(id=self.kwargs['pk']))
        return super(NewsletterUpdateView, self).get_context_data(**kwargs)
    

class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = AddNewsletterForm
    template_name = 'newsletters/newsletter_create.html'
    success_url = 'aciu'
      
def send(request, *args, **kwargs):
    logger.info(u'Preparing to send newsletter.')
            
    upcoming_events = Event.public.filter(
                                   Q(end_date__isnull = False) & Q(end_date__gt = timezone.now()) |
                                   Q(start_date__gt = timezone.now())
                                   )
    logger.info(u'{0} upcoming events'.format(upcoming_events.count()))
    
    recent_articles = Article.public.order_by('-create_date')[:3]
    logger.info(u'{0} recent articles'.format(recent_articles.count()))
    
    recent_announcements = Announcement.public.order_by('-create_date')[:3]
    logger.info(u'{0} recent announcements'.format(recent_announcements.count()))
        
    recent_galleries = Gallery.objects.filter(is_public=True)[:3]
    logger.info(u'{0} recent galleries'.format(recent_galleries.count()))
    
    recent_classifieds = Classified.public.order_by('-create_date')[:3]
    logger.info(u'{0} recent classifieds'.format(recent_classifieds.count())) 
    
    newsletter = Newsletter.objects.get(id=kwargs['pk'])        
    subject = u'Artimiausi renginiai Niujorke'
    
    c = Context({
                 'event_list' : upcoming_events,
                 'article_list': recent_articles,
                 'gallery_list': recent_galleries,
                 'announcement_list': recent_announcements,
                 'classified_list': recent_classifieds,
                 'newsletter': newsletter,
                 'SITE_URL': settings.SITE_URL,
                 'google_analytics': '?utm_source=newsletter&utm_medium=email&utm_campaign=newsletter',
                 'google_analytics_event_heading': '?utm_source=newsletter&utm_medium=email&utm_campaign=newsletter&utm_content=heading',
                 'google_analytics_event_description': '?utm_source=newsletter&utm_medium=email&utm_campaign=newsletter&utm_content=description',
                 })

    plainText = get_template('newsletters/newsletter_detail.txt').render(c)
    htmlText = get_template('newsletters/newsletter_detail.html').render(c)

    subscribers = SiteUser.objects.filter(is_subscribed=True).order_by('email').values_list('email', flat=True)
    logger.info(u'{0} subscribers'.format(subscribers.count()))
    split = int(ceil(len(subscribers)/50.))
    split_sets = [subscribers[i * split : (i+1) * split] for i in range(50)] 
     
    i = 0
    for recipients in split_sets:
        logger.info(u'Scheduling a task for {0}'.format(timezone.now() + timezone.timedelta(minutes=10*i+1)))
        logger.debug(u'Will e-mail these addresses: {0}'.format(recipients))
        send_newsletter.apply_async((subject, settings.EVENTS_PRIMARY_EMAIL, recipients, plainText, htmlText), countdown = 60*(10*i+1))
        i += 1
     
    return render_to_response('events/success.html', {
                                                      'message': 'Naujienlaiškis išsiųstas sėkmingai.',
                                                      }, context_instance=RequestContext(request))
    
#     split = int(ceil(len(subscribers)/10.))
#     split_sets = [subscribers[i * split : (i+1) * split] for i in range(10)]
#     for recipients in split_sets: 
#         emails = [{
#                    'recipients': [x],
#                    'sender': settings.EVENTS_PRIMARY_EMAIL,
#                    'message': plainText,
#                    'html_message': htmlText,
#                    'subject': subject,
#                    'log_level': 2
#                    } for x in recipients]
#         mail.send_many(emails)
    
#     i = 0  
#     for subscriber in subscribers:
#         logger.debug(u'E-mailing newsletter to {0}'.format(subscriber))
#         mail.send(
#                   recipients=(subscriber,),
#                   sender=settings.EVENTS_PRIMARY_EMAIL,
#                   message=plainText,
#                   html_message=htmlText,
#                   subject=subject,
#                   log_level=2,
#                   scheduled_time = timezone.now() + timezone.timedelta(minutes=int(floor(i/10.)))
#                   )
#         i += 1
    
def test_send(request, *args, **kwargs):
    logger.info(u'Preparing to test-send newsletter.')
            
    upcoming_events = Event.public.filter(
                                   Q(end_date__isnull = False) & Q(end_date__gt = timezone.now()) |
                                   Q(start_date__gt = timezone.now())
                                   )
    logger.info(u'{0} upcoming events'.format(upcoming_events.count()))
    
    recent_articles = Article.public.order_by('-create_date')[:3]
    logger.info(u'{0} recent articles'.format(recent_articles.count()))
    
    recent_announcements = Announcement.public.order_by('-create_date')[:3]
    logger.info(u'{0} recent announcements'.format(recent_announcements.count()))
        
    recent_galleries = Gallery.objects.filter(is_public=True)[:3]
    logger.info(u'{0} recent galleries'.format(recent_galleries.count()))
    
    recent_classifieds = Classified.public.order_by('-create_date')[:3]
    logger.info(u'{0} recent classifieds'.format(recent_classifieds.count())) 
    
    newsletter = Newsletter.objects.get(id=kwargs['pk'])        
    subject = u'Artimiausi renginiai Niujorke'
    
    c = Context({
                 'event_list' : upcoming_events,
                 'article_list': recent_articles,
                 'gallery_list': recent_galleries,
                 'announcement_list': recent_announcements,
                 'classified_list': recent_classifieds,
                 'newsletter': newsletter,
                 'SITE_URL': settings.SITE_URL,
                 'google_analytics': '?utm_source=newsletter&utm_medium=email&utm_campaign=newsletter',
                 'google_analytics_event_heading': '?utm_source=newsletter&utm_medium=email&utm_campaign=newsletter&utm_content=heading',
                 'google_analytics_event_description': '?utm_source=newsletter&utm_medium=email&utm_campaign=newsletter&utm_content=description',
                 })

    plainText = get_template('newsletters/newsletter_detail.txt').render(c)
    htmlText = get_template('newsletters/newsletter_detail.html').render(c)
    
    subscribers = ('algirdas.grybas@gmail.com', 'info@nylithuanian.org', 'events@nylithuanian.org')
    logger.info(u'{0} subscribers'.format(len(subscribers)))
    subscribers = SiteUser.objects.filter(is_subscribed=True).order_by('email').values_list('email', flat=True)
    logger.info(u'{0} subscribers'.format(subscribers.count()))
    split = int(ceil(len(subscribers)/50.))
    split_sets = [subscribers[i * split : (i+1) * split] for i in range(50)] 
      
    i = 0
    for recipients in split_sets:
        logger.info(u'Scheduling a task for {0}'.format(timezone.now() + timezone.timedelta(minutes=10*i+1)))
        logger.debug(u'Will e-mail these addresses: {0}'.format(recipients))
        test_send_newsletter.apply_async((subject, settings.EVENTS_PRIMARY_EMAIL, recipients, plainText, htmlText), countdown = 60*(10*i+1))
        i += 1

#     i = 0
#     for subscriber in subscribers:
#         logger.debug(u'E-mailing newsletter to {0}'.format(subscriber))
#         mail.send(
#                   recipients=(subscriber,),
#                   sender=settings.EVENTS_PRIMARY_EMAIL,
#                   message=plainText,
#                   html_message=htmlText,
#                   subject=subject,
#                   log_level=2,
#                   scheduled_time = timezone.now() + timezone.timedelta(minutes=int(floor(i/10.)))
#                   )
#         i += 1
        
    return render_to_response('events/success.html', {
                                                      'message': 'Naujienlaiškis išsiųstas sėkmingai.',
                                                      }, context_instance=RequestContext(request))
