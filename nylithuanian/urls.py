#encoding=utf-8
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView, CreateView
from views import HomeView
from django.conf.urls.static import static

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
    url(r'^nuotraukos/', include('photos.urls'), {'active_tab': 'nuotraukos'}),
    url(r'^skelbimai/', include('classifieds.urls'), {'active_tab': 'skelbimai'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<active_tab>renginiai)/', include('events.urls')),
    url(r'^(?P<active_tab>straipsniai)/', include('articles.urls')),
    url(r'^nariai/', include('users.urls')),
    url(r'^(?P<active_tab>sveikinimai)/', include('greetings.urls')),
    url(r'^(?P<active_tab>uzuojautos)/', include('sympathies.urls')),
    url(r'^media/(?P<path>.*)/$', 'django.views.static.serve', { 'document_root' : settings.MEDIA_ROOT }),
    url(r'^apie-mus/$', TemplateView.as_view(template_name='flatpages/about_us.html'), { 'active_tab': 'apie-mus' }),
    url(r'^apie-mus/apygarda/$', TemplateView.as_view(template_name='flatpages/apygarda.html'), { 'active_tab': 'apie-mus' }),
    url(r'^apie-mus/long-island-apylinke/$', TemplateView.as_view(template_name='flatpages/li.html'), { 'active_tab': 'apie-mus' }),
    url(r'^apie-mus/new-york-miesto-apylinke/$', TemplateView.as_view(template_name='flatpages/nyc.html'), { 'active_tab': 'apie-mus' }),
    url(r'^apie-mus/rytinio-long-island-apylinke/$', TemplateView.as_view(template_name='flatpages/rli.html'), { 'active_tab': 'apie-mus' }),
    url(r'^apie-mus/rochester-apylinke/$', TemplateView.as_view(template_name='flatpages/rochester.html'), { 'active_tab': 'apie-mus' })
                       
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
