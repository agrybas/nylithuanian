#encoding=utf-8
from django.views.generic import TemplateView
from events.models import Event
from articles.models import Article
from photos.models import Gallery
from announcements.models import Announcement
from users.models import SiteUser
from classifieds.models import Classified
from django.utils import timezone
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from forms import SendEmailForm
from django.contrib.admin.views.decorators import staff_member_required

import logging
import settings
import pytz

if settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['upcoming_events'] = Event.public.filter(start_date__gte=timezone.now()).order_by('start_date')
        context['articles'] = Article.public.order_by('-create_date')[:3]
        context['announcements'] = Announcement.public.order_by('-create_date')[:3]
        context['classifieds'] = Classified.public.order_by('-create_date')[:5]
        context['photo_albums'] = Gallery.objects.filter(is_public=True).order_by('-date_added')[:5]
        context['cutoff_time'] = timezone.datetime(2014,5,25,17,0,0, tzinfo=timezone.utc)
        context['current_time'] = timezone.now()
#        context['user_count'] = SiteUser.objects.filter(is_active=True).count()
        return context
    