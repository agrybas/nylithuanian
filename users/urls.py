from django.conf.urls import patterns, url
from django.views.generic import ListView, CreateView, TemplateView
from models import UserProfile, User
from forms import RegisterUserForm
from views import UserDetailView, confirm_registration
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
                                model = UserProfile,
                                #template_name = 'users/user_list.html'
                                )),
    url(r'^registruotis/$', CreateView.as_view(
                                               template_name = 'users/register.html',
                                               form_class = RegisterUserForm,
                                               model = User,
                                               success_url = '/nariai/registruotis/priimta'
                                         )),
    url(r'^registruotis/priimta/$', TemplateView.as_view(
                                                         template_name = 'users/registration_accepted.html',
                                                         )),
    url(r'^patvirtinti/(?P<username>\w+)/(?P<registrationHash>\S+)/$', confirm_registration),
    url(r'^prisijungti/$', login, {
                                  'template_name' : 'users/login.html',
                                  }),
    url(r'^atsijungti/$', logout, {
                                   'next_page' : '/',
                                   }),
    url(r'^(?P<slug>\w+)/$', UserDetailView.as_view()),

)