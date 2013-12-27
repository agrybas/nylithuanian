#encoding=utf-8
from django.conf.urls import patterns, url
from django.views.generic import DetailView
from views import SympathyCreateView, SympathyUpdateView, SympathyCommentCreateView, SympathyDetailView, SympathyListView
from models import Sympathy
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^$', SympathyListView.as_view()),
    url(r'^pateikti/$', login_required(login_url='/nariai/prisijungti')(SympathyCreateView.as_view())),
    url(r'^(?P<pk>\d+)/$', SympathyDetailView.as_view()),
    url(r'^(?P<pk>\d+)/redaguoti/$', SympathyUpdateView.as_view()),
    url(r'^(?P<pk>\d+)/komentarai/$', SympathyCommentCreateView.as_view()),
)
