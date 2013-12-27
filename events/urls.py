#encoding=utf-8
from django.conf.urls import patterns, url
from views import UpcomingEventsListView, PastEventsListView, CommentCreateView, \
                    EventDetailView, EventCreateView, EventAttachmentListView, EventUpdateView, EventRssView, \
                    create_reminder, delete_reminder
from django.contrib.auth.decorators import login_required


urlpatterns = patterns('',
    url(r'^$', UpcomingEventsListView.as_view()),
#    url(r'^pateikti/$', login_required(login_url='/nariai/prisijungti')(EventPreview(AddEventForm))),
    url(r'^pateikti/$', login_required(login_url='/nariai/prisijungti')(EventCreateView.as_view())),
    url(r'^archyvas/$', PastEventsListView.as_view()),
    url(r'^rss/$', EventRssView()),
    url(r'^(?P<pk>\d+)/redaguoti/$', EventUpdateView.as_view()),
    url(r'^(?P<pk>\d+)/komentarai/$', CommentCreateView.as_view()),
    url(r'^(?P<pk>\d+)/prisegtukai/$', EventAttachmentListView.as_view()),
    url(r'^(?P<pk>\d+)/zemelapis/$', EventDetailView.as_view(template_name='events/event_map.html')),
    url(r'^(?P<pk>\d+)/priminti/$', login_required(login_url='/nariai/prisijungti')(create_reminder)),
    url(r'^(?P<pk>\d+)/nepriminti/$', login_required(login_url='/nariai/prisijungti')(delete_reminder)),
    url(r'^(?P<pk>\d+)/$', EventDetailView.as_view()),
)

