#encoding=utf-8
import os
from celery import app
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, UpdateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from models import Event, EventComment, EventAttachment, EventReminder, Venue
from tasks import send_reminder
from forms import AddEventForm, AddEventCommentForm
from photos.models import Photo, Gallery
from articles.models import Article
from django.template.loader import get_template
from django.core.mail import mail_admins, EmailMultiAlternatives
from django.core import serializers

import logging
import nylithuanian.settings
from django.views.generic.edit import FormView
from django.db.models import Q

if nylithuanian.settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)


class UpcomingEventsListView(ListView):
    model = Event
#     queryset = Event.public.filter(start_date__gte=timezone.now()).order_by('start_date')
    paginate_by = 5
    
    def get_queryset(self):
        return Event.public.filter(
                                   Q(end_date__isnull = False) & Q(end_date__gt = timezone.now()) |
                                   Q(start_date__gt = timezone.now())
                                   )
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        kwargs['headline'] = 'Artimiausi renginiai'
        return super(UpcomingEventsListView, self).get_context_data(**kwargs) 

#@cache_control(must_revalidate=True, max_age=3600)
class PastEventsListView(ListView):
    model = Event
#     queryset = Event.public.filter(start_date__lt=timezone.now()).order_by('-start_date')
    paginate_by = 5
    
    def get_queryset(self):
        return Event.public.filter(
                                   Q(end_date__isnull = False) & Q(end_date__lt = timezone.now()) |
                                   Q(start_date__lt=timezone.now())
                                   ).order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        kwargs['headline'] = 'Praėjusių renginių sąrašas'
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(PastEventsListView, self).get_context_data(**kwargs)
        
class EventDetailView(DetailView):
    model = Event
    
    def get_context_data(self, **kwargs):
        kwargs['comment_count'] = EventComment.objects.filter(event=self.kwargs['pk']).count()
        kwargs['attachment_count'] = EventAttachment.objects.filter(event=self.kwargs['pk']).count()
        kwargs['photo_count'] = Photo.objects.filter(is_public=True).filter(gallery__event_id__exact=self.kwargs['pk']).count()
        kwargs['has_reminder'] = EventReminder.objects.filter(user_id=self.request.user.id).filter(event_id=self.kwargs['pk']).exists()
        event = Event.objects.get(id=self.kwargs['pk'])
        kwargs['is_upcoming'] = event.start_date > timezone.now() + timedelta(hours=24)
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(EventDetailView, self).get_context_data(**kwargs)
    
class EventCreateView(CreateView):
    model = Event
    form_class = AddEventForm
    template_name = 'events/event_create.html'
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'events/attachments'))
    success_url = 'aciu'
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(EventCreateView, self).get_context_data(**kwargs)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(EventCreateView, self).form_valid(form)    
    
class EventAttachmentListView(ListView):
    def get_queryset(self):
        return EventAttachment.objects.filter(event=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        kwargs['headline'] = 'Prisegtukai'
        kwargs['event'] = Event.objects.get(id=self.kwargs['pk'])
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(EventAttachmentListView, self).get_context_data(**kwargs)


class UserOwnedObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        obj = super(UserOwnedObjectMixin, self).get_object(queryset)
        if self.request.user.is_staff:
            return obj
        if obj.user_id != self.request.user.id:
            raise PermissionDenied
        return obj
    
class EventUpdateView(UserOwnedObjectMixin, UpdateView):
    model = Event
    form_class = AddEventForm
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'events/attachments'))
    success_url = '../'
    template_name = 'events/event_edit.html'
    

    @method_decorator(login_required(login_url='/nariai/prisijungti'))
    def dispatch(self, *args, **kwargs):
        return super(EventUpdateView, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        saved_event = Event.objects.get(id=self.kwargs['pk'])
        
        # check if start_date or end_date is changed -- needed for ICS calendar generation
        if (saved_event.start_date != form.instance.start_date) or (saved_event.end_date != form.instance.end_date):
            form.instance.version_number += 1
        
        form.instance.user = self.request.user # TO-DO: don't change ownership when event is updated
        return super(EventUpdateView, self).form_valid(form)
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(EventUpdateView, self).get_context_data(**kwargs)
    
class EventRssView(Feed):
    title = 'Lietuvių renginiai Niujorke'
    link = '/renginiai/'
    description = 'Artimiausi lietuvių renginiai, vykstantys Niujorko valstijoje bei kaimyninėse bendruomenėse.'
    description_template = 'feeds/rss_description.html'
    
    def items(self):
        # return Event.public.filter(start_date__gte=timezone.now()).order_by('start_date')
        return Event.public.filter(
                                   Q(end_date__isnull = False) & Q(end_date__gt = timezone.now()) |
                                   Q(start_date__gt = timezone.now())
                                   )
    def item_title(self, item):
        return item.title  
    
    def item_description(self, item):
        if len(item.body) <= 1000:
            return item.body
        return item.body[:1000].rsplit(' ', 1)[0] + '...'

    def item_link(self, item):
        return item.get_absolute_url() + '?utm_source=feed&utm_medium=rss'
    
class CommentCreateView(CreateView):
    form_class = AddEventCommentForm
    model = EventComment
    template_name = 'event_comments/comment_create.html'
    success_url = '.'
    
    def get_context_data(self, **kwargs):
        kwargs['comment_list'] = EventComment.objects.filter(event=self.kwargs['pk']).order_by('-create_date')
        kwargs['attachment_count'] = EventAttachment.objects.filter(event=self.kwargs['pk']).count
        kwargs['event'] = Event.objects.get(id=self.kwargs['pk'])
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(CommentCreateView, self).get_context_data(**kwargs)
    
    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        form.instance.event_id = self.kwargs['pk']
        return super(CommentCreateView, self).form_valid(form)
    
def create_reminder(request, *args, **kwargs):
    try:
        logger.info(u'User {0} is creating a reminder for event_id={1}...'.format(request.user.username, kwargs['pk']))
        
        # check if the reminder already exists
        if EventReminder.objects.filter(user_id=request.user.id).filter(event_id=kwargs['pk']).exists():
            logger.info(u'Reminder for this event already exists. Aborting...')
            return render_to_response('events/error.html', {
                                                          'message': u'Jūs jau turite priminimą apie šį renginį. Priminimas bus išsiųstas Jums el. paštu likus 24 valandoms iki renginio pradžios.',
                                                          }, context_instance=RequestContext(request))

        # get the event
        event = Event.objects.get(id=kwargs['pk'])
        logger.debug(u'Found event "{0}"'.format(event.title))
        
        # calculate reminder date (24 hours before the event)
        remind_date =  event.start_date - timedelta(hours=24)
        logger.debug(u'Event start date: {0}'.format(event.start_date))
        logger.debug(u'Remind date: {0}'.format(remind_date))
        
        # check if reminder date is in the future
        if remind_date < timezone.now():
            logger.warning(u'Requested remind_date is in the past. Aborting...')
            return render_to_response('events/error.html', {
                                                          'message': u'Priminimą galima užsisakyti iki renginio pradžios likus bent 24 valandoms. Ar šis renginys įvyks bent po 24 valandų?',
                                                          }, context_instance=RequestContext(request))        
        
        # create celery reminder task
        result = send_reminder.apply_async(queue='events', eta=remind_date,
                                           kwargs={
                                                   'recipient_email': request.user.email,
                                                   'event': event,
                                                   })
        
        # update database with a new pending task
        reminder = EventReminder(event_id=event.id, user_id=request.user.id, remind_date=remind_date, task_id=result.task_id)
        reminder.save()
        logger.info(u'Reminder set on {0} successfully.'.format(reminder.remind_date))
        
        return render_to_response('events/success.html', {
                                                          'message': u'Priminimas išsaugotas sėkmingai. Likus 24 valandoms iki renginio pradžios, informuosime Jus el. pašto adresu {0}'.format(request.user.email)
                                                          }, context_instance=RequestContext(request))
    except Event.DoesNotExist:
        logger.exception(u'Exception thrown while creating reminder for event_id={0}:'.format(kwargs['pk']))
        raise Http404        
    except Exception:
        logger.exception(u'Exception thrown while creating a reminder for event_id={0}:'.format(kwargs['pk']))
        return render_to_response('events/error.html', {
                                                          'message': u'Bandant išsaugoti priminimą, įvyko klaida. Svetainės administratoriai apie tai jau informuoti. Atsiprašome už nepatogumus.',
                                                          }, context_instance=RequestContext(request))
        
def delete_reminder(request, *args, **kwargs):
    try:
        logger.info(u'User {0} is deleting a reminder for event_id={1}...'.format(request.user.username, kwargs['pk']))
        
        # get the reminder from database
        reminder = EventReminder.objects.filter(user_id=request.user.id).filter(event_id=kwargs['pk'])[0]
        logger.debug(u'Found task_id={0}'.format(reminder.task_id))
        
        if not reminder.task_id:
            logger.info(u'Reminder for this event does not exist. Aborting...')
            return render_to_response('events/error.html', {
                                                          'message': u'Jūs neturite užsisakę priminimo šiam renginiui.',
                                                          }, context_instance=RequestContext(request))
        
        # revoke celery reminder task
        app.control.revoke(reminder.task_id, terminate=True)
        
        # delete associated reminder entry in the database
        reminder.delete()
        
        logger.info(u'Reminder deleted successfully.')
        return render_to_response('events/success.html', {
                                                          'message': u'Priminimas pašalintas sėkmingai.',
                                                          }, context_instance=RequestContext(request))
    except Exception:
        logger.exception(u'Exception thrown while deleting a reminder for event_id={0}:'.format(kwargs['pk']))
        return render_to_response('events/error.html', {
                                                          'message': u'Bandant pašalinti priminimą, įvyko klaida. Svetainės administratoriai apie tai jau informuoti. Atsiprašome už nepatogumus.',
                                                          }, context_instance=RequestContext(request))
        
def approve(request, *args, **kwargs):
    try:
        logger.info(u'Staff user {0} is approving event id={1}'.format(request.user.username, kwargs['pk']))
        
        event = Event.objects.get(id=kwargs['pk'])
        event.is_approved = True
        event.save()
        
        logger.info(u'Event {0} approved successfully'.format(kwargs['pk']))
        
        # inform event creator
        plainText = get_template('emails/event_approved.txt')
        htmlText = get_template('emails/event_approved.html')
        subject = u'Pranešimas apie renginį patvirtintas'
        c = Context({ 'event' : event })
        msg = EmailMultiAlternatives(subject, plainText.render(c), settings.SERVER_EMAIL, (event.user.email, ))
        msg.attach_alternative(htmlText.render(c), 'text/html')
        msg.send()
        
        return render_to_response('events/success.html', {
                                                          'message': u'Renginys patvirtintas sėkmingai. Renginio pranešėjas apie tai informuotas el. paštu.',
                                                          }, context_instance=RequestContext(request))
    
    except Exception:
        logger.exception(u'Exception thrown while approving event id {0}:'.format(kwargs['pk']))
        return render_to_response('events/error.html', {
                                                          'message': u'Renginio nepavyko patvirtinti. Prašome patikrinti, ar šis renginys egzistuoja ir tikrai laukia patvirtinimo. Svetainės administratoriai apie tai jau informuoti.',
                                                          }, context_instance=RequestContext(request))

    
def get_venues_list(request, *args, **kwargs):
    try:
        logger.info('Loading the list of venues...')
        venues = Venue.objects.all()
        json_data = serializers.serialize('json', venues,
                                          fields= (
                                                   'title',
                                                   'street_address1',
                                                   'street_address2',
                                                   'street_address3',
                                                   'city',
                                                   'zip_code',
                                                   'state',
                                                   'country'
                                                   ))
        logger.info(json_data)
        logger.info('List loaded successfully.')
        return HttpResponse(json_data, content_type='application/json')
    except Venue.DoesNotExist:
        return HttpResponse('')