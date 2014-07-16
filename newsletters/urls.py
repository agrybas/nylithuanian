#encoding=utf-8
from django.conf.urls import patterns, url
# from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView

import views

urlpatterns = patterns('',
    url(r'^$', staff_member_required(views.NewsletterListView.as_view())),
    url(r'^pateikti/aciu/$', staff_member_required(TemplateView.as_view(template_name='newsletters/newsletter_create_success.html'))),
    url(r'^pateikti/$', staff_member_required(views.NewsletterCreateView.as_view())),
    url(r'^(?P<pk>\d+)/redaguoti/$', staff_member_required(views.NewsletterUpdateView.as_view())),
    url(r'^(?P<pk>\d+)/siusti/$', staff_member_required(views.send)),
    url(r'^(?P<pk>\d+)/siusti-test/$', staff_member_required(views.test_send)),
    # url(r'^(?P<pk>\d+)/patvirtinti/$', staff_member_required(views.approve)),
    url(r'^(?P<pk>\d+)/$', staff_member_required(views.NewsletterDetailView.as_view())),
)