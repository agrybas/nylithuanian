from django.conf.urls import patterns, url
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.views import login, logout

from models import SiteUser
from forms import RegisterSiteUserForm
from views import SiteUserCreateView, SiteUserDetailView, SiteUserUpdateView, confirm_registration

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model = SiteUser,)),
#    url(r'^mano-saskaita/$', SiteUserPersonalView.as_view()),
    url(r'^registruotis/$', SiteUserCreateView.as_view()),
    url(r'^registruotis/priimta/$', TemplateView.as_view(template_name = 'users/registration_accepted.html',)),
    url(r'^patvirtinti/(?P<username>\w+)/(?P<registrationHash>\S+)/$', confirm_registration),
    url(r'^prisijungti/$', login, { 'template_name' : 'users/login.html', }),
    url(r'^atsijungti/$', logout, { 'next_page' : '/', }),
    url(r'^(?P<slug>\w+)/$', SiteUserDetailView.as_view()),
    url(r'^(?P<slug>\w+)/redaguoti/$', SiteUserUpdateView.as_view()),
)