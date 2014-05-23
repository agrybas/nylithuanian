#encoding=utf-8
from django.conf.urls import patterns, url
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.views import login, logout, password_reset, password_reset_confirm, password_reset_done, password_reset_complete

from models import SiteUser
from forms import RegisterSiteUserForm
from views import SiteUserCreateView, SiteUserDetailView, SiteUserChangePasswordView, SiteUserUpdateView, confirm_registration

urlpatterns = patterns('',
#    url(r'^$', ListView.as_view(model = SiteUser,)),
#    url(r'^mano-saskaita/$', SiteUserPersonalView.as_view()),
    url(r'^pamirsau-slaptazodi/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {
                                                                                                   'template_name': 'users/password_reset_confirm.html',
                                                                                                   'post_reset_redirect': '/nariai/pamirsau-slaptazodi/baigta'
                                                                                                   }),
    url(r'^pamirsau-slaptazodi/baigta/$', password_reset_complete, {
                                                                    'template_name': 'users/password_reset_complete.html'
                                                                    }),
    url(r'^pamirsau-slaptazodi/email/$', password_reset_done, {
                                                               'template_name': 'users/password_reset_done.html'
                                                               }),
    url(r'^pamirsau-slaptazodi/$', password_reset, {
                                                    'template_name': 'users/password_reset_form.html',
                                                    'email_template_name': 'emails/password_reset.html',
                                                    'subject_template_name': 'emails/password_reset_subject.txt',
                                                    'post_reset_redirect': '/nariai/pamirsau-slaptazodi/email'
                                                    }),
    url(r'^registruotis/$', SiteUserCreateView.as_view()),
    url(r'^registruotis/priimta/$', TemplateView.as_view(template_name = 'users/registration_accepted.html',)),
    url(r'^patvirtinti/(?P<username>\S+)/(?P<registrationHash>\S+)/$', confirm_registration),
    url(r'^prisijungti/$', login, {
                                   'template_name' : 'users/login.html',
                                   }),
    url(r'^atsijungti/$', logout, { 'next_page' : '/', }),
    url(r'^(?P<slug>\S+)/keisti-slaptazodi/$', SiteUserChangePasswordView.as_view()),
    url(r'^(?P<slug>\S+)/redaguoti/$', SiteUserUpdateView.as_view()),
    url(r'^(?P<slug>\S+)/$', SiteUserDetailView.as_view()),
)