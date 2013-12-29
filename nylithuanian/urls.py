#encoding=utf-8
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView, CreateView
from photologue.models import Photo
from views import HomeView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'nylithuanian.views.home', name='home'),
    # url(r'^nylithuanian/', include('nylithuanian.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^$', HomeView.as_view()),
    url(r'^stop/$', TemplateView.as_view(template_name = 'stop.html')),
    url(r'^home/', RedirectView.as_view(url='/')),
    url(r'^nuotraukos/photo/add/$', CreateView.as_view(model=Photo), name='add-photo'),
    url(r'^nuotraukos/', include('photologue.urls'), { 'active_tab': 'nuotraukos' }),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<active_tab>renginiai)/', include('events.urls')),
    url(r'^(?P<active_tab>straipsniai)/', include('articles.urls')),
    url(r'^nariai/', include('users.urls')),
    url(r'^(?P<active_tab>sveikinimai)/', include('greetings.urls')),
    url(r'^(?P<active_tab>uzuojautos)/', include('sympathies.urls')),
    url(r'^media/(?P<path>.*)/$', 'django.views.static.serve', {
                                                               'document_root' : settings.MEDIA_ROOT
                                                               }),
)
