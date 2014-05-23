#encoding=utf-8
from smtplib import SMTPException
from math import ceil
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

from events.models import Event
from articles.models import Article
from photos.models import Gallery
from users.models import SiteUser
from classifieds.models import Classified
from announcements.models import Announcement

from .models import Newsletter
from .forms import AddNewsletterForm

if not settings.DEBUG:
    from .tasks import send_newsletter

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
        kwargs['event_list'] = Event.public.filter(start_date__gte=timezone.now()).order_by('start_date')
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
            
    upcoming_events = Event.public.filter(start_date__gte=timezone.now()).order_by('start_date')
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
      
    subscribers = SiteUser.objects.filter(is_subscribed=True).values_list('email', flat=True)
    logger.info(u'{0} subscribers'.format(subscribers.count()))
    
    plainText = get_template('newsletters/newsletter_detail.txt')
    htmlText = get_template('newsletters/newsletter_detail.html')
    subject = u'Artimiausi renginiai Niujorke'
    from_address = 'events@nylithuanian.org'
    
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
       
    conn = get_connection()
    conn.open() # open single SMTP connection to use for mass email
    
    for to_address in subscribers:
        try:
            msg = EmailMultiAlternatives(subject, plainText.render(c), from_address, to=(to_address,), connection=conn)
            msg.attach_alternative(htmlText.render(c), 'text/html')
            msg.send(fail_silently=False)
        except SMTPException:
            logger.error(u'An SMTP error occurred while sending email to {0}'.format(to_address))
        
    conn.close() # no more emails to send -- close connection
    logger.info(u'Newsletter sent successfully.')
  
    return render_to_response('events/success.html', {
                                                      'message': 'Naujienlaiškis išsiųstas sėkmingai.',
                                                      }, context_instance=RequestContext(request))
    
def send_test(request, *args, **kwargs):
    logger.info(u'Preparing to test-send newsletter.')
            
    upcoming_events = Event.public.filter(start_date__gte=timezone.now()).order_by('start_date')
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
    
#     subscribers = ['algirdas.grybas@gmail.com', 'agrybas@nylithuanian.org']
#     logger.info(u'{0} subscribers'.format(len(subscribers)))
    subscribers = SiteUser.objects.filter(is_subscribed=True).values_list('email', flat=True)
    logger.info(u'{0} subscribers'.format(subscribers.count()))
    subscribers = list(subscribers.all())
    split = int(ceil(len(subscribers)/4.))
    split_sets = [subscribers[i * split : (i+1) * split] for i in range(4)] 
    
    for recipients in split_sets:
        send_newsletter.apply_async((subject, settings.EVENTS_PRIMARY_EMAIL, recipients, plainText, htmlText), countdown = random.randint(0, 100))
    
    return render_to_response('events/success.html', {
                                                      'message': 'Naujienlaiškis išsiųstas sėkmingai.',
                                                      }, context_instance=RequestContext(request))
