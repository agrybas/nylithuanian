#encoding=utf-8
from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from views import ClassifiedCategoriesListView, ClassifiedCreateView, ClassifiedsListView, ClassifiedDetailView, ClassifiedUpdateView
from django.views.generic import TemplateView

urlpatterns = patterns('',
                       url(r'^$', ClassifiedCategoriesListView.as_view()),
                       url(r'^(?P<pk>\d+)/$', ClassifiedDetailView.as_view()),
                       url(r'^(?P<pk>\d+)/redaguoti/$', login_required(login_url='/nariai/prisijungti')(ClassifiedUpdateView.as_view())),
                       url(r'^kategorijos/(?P<pk>\d+)/$', ClassifiedsListView.as_view()),
                       url(r'^pateikti/$', login_required(login_url='/nariai/prisijungti')(ClassifiedCreateView.as_view())),
                       url(r'^pateikti/aciu/$', TemplateView.as_view(template_name='classifieds/classified_create_success.html')),
    )