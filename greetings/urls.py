#encoding=utf-8
from django.conf.urls import patterns, url
from django.views.generic import DetailView
from views import GreetingCommentCreateView, GreetingCreateView, GreetingUpdateView, GreetingDetailView, GreetingListView
from models import Greeting
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^$', GreetingListView.as_view()),
    url(r'^pateikti/$', login_required(login_url='/nariai/prisijungti')(GreetingCreateView.as_view())),
    url(r'^(?P<pk>\d+)/$', GreetingDetailView.as_view()),
    url(r'^(?P<pk>\d+)/redaguoti/$', GreetingUpdateView.as_view()),
    url(r'^(?P<pk>\d+)/komentarai/$', GreetingCommentCreateView.as_view()),
)
