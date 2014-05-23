#encoding=utf-8
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
import views
import feeds


urlpatterns = patterns('',
    url(r'^$', views.UpcomingEventsListView.as_view()),
#    url(r'^pateikti/$', login_required(login_url='/nariai/prisijungti')(views.EventPreview(AddEventForm))),
    url(r'^pateikti/aciu/$', TemplateView.as_view(template_name='events/event_create_success.html')),
    url(r'^pateikti/$', login_required(login_url='/nariai/prisijungti')(views.EventCreateView.as_view())),
    url(r'^archyvas/$', views.PastEventsListView.as_view()),
    url(r'^get-venues-list/$', views.get_venues_list),
    url(r'^rss/$', views.EventRssView()),
    url(r'^(?P<pk>\d+)/redaguoti/$', views.EventUpdateView.as_view()),
    url(r'^(?P<pk>\d+)/komentarai/$', views.CommentCreateView.as_view()),
    url(r'^(?P<pk>\d+)/prisegtukai/$', views.EventAttachmentListView.as_view()),
    url(r'^(?P<pk>\d+)/zemelapis/$', views.EventDetailView.as_view(template_name='events/event_map.html')),
    url(r'^(?P<pk>\d+)/patvirtinti/$', views.approve),
    url(r'^(?P<pk>\d+)/priminti/$', login_required(login_url='/nariai/prisijungti')(views.create_reminder)),
    url(r'^(?P<pk>\d+)/nepriminti/$', login_required(login_url='/nariai/prisijungti')(views.delete_reminder)),
    
    url(r'^(?P<pk>\d+)/$', views.EventDetailView.as_view()),
)

urlpatterns += patterns('',
    url(r'^(?P<pk>\d+)/kalendorius/$', feeds.getEventIcsFeed),
    )