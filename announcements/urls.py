#encoding=utf-8
from django.conf.urls import patterns, url
from django.views.generic import ListView
from views import  AnnouncementDetailView,  AddAnnouncementPreview, AnnouncementUpdateView, AnnouncementListView
from forms import AddAnnouncementForm
from models import Announcement
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^$', AnnouncementListView.as_view()),
    url(r'^pateikti/$', login_required(login_url='/nariai/prisijungti')(AddAnnouncementPreview(AddAnnouncementForm))),                        
    url(r'^(?P<pk>\d+)/$', AnnouncementDetailView.as_view()),
    url(r'^(?P<pk>\d+)/redaguoti/$', AnnouncementUpdateView.as_view()),
)
