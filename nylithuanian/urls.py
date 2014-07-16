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
    url(r'^home/', RedirectView.as_view(url='/')),
    url(r'^stop/$', TemplateView.as_view(template_name = 'stop.html')),
    url(r'^nuotraukos/', include('photos.urls'), {'active_tab': 'nuotraukos'}),
    url(r'^skelbimai/', include('classifieds.urls'), {'active_tab': 'skelbimai'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^renginiai/', include('events.urls'), {'active_tab': 'renginiai'}),
    url(r'^straipsniai/', include('articles.urls'), {'active_tab': 'straipsniai'}),
    url(r'^pranesimai/', include('announcements.urls'), {'active_tab': 'pranesimai'}),
    url(r'^nariai/', include('users.urls')),
    url(r'^naujienlaiskiai/', include('newsletters.urls')),
#    url(r'^(?P<active_tab>sveikinimai)/', include('greetings.urls')),
#    url(r'^(?P<active_tab>uzuojautos)/', include('sympathies.urls')),
    url(r'^media/(?P<path>.*)/$', 'django.views.static.serve', { 'document_root' : settings.MEDIA_ROOT }),
                       
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Apie mus section
urlpatterns += patterns('',
    url(r'^apie-mus/$', TemplateView.as_view(template_name='flatpages/about_us.html'), { 'active_tab': 'apie-mus' }),
    url(r'^apie-mus/susitelkimo-centrai/$', TemplateView.as_view(template_name='flatpages/susitelkimo_centrai.html'), { 'active_tab': 'apie-mus', 'active_item': 'susitelkimo-centrai' }),
    url(r'^apie-mus/apie-jav-lb/$', TemplateView.as_view(template_name='flatpages/apie_jav_lb.html'), { 'active_tab': 'apie-mus', 'active_item': 'apie-jav-lb' }),
    url(r'^apie-mus/prisijunk/$', TemplateView.as_view(template_name='flatpages/prisijunk.html'), { 'active_tab': 'apie-mus', 'active_item': 'prisijunk' }),
    url(r'^apie-mus/parama/$', TemplateView.as_view(template_name = 'flatpages/parama.html'), {'active_tab': 'apie-mus', 'active_item': 'parama'}),
    url(r'^apie-mus/apygarda/$', TemplateView.as_view(template_name='flatpages/apygarda.html'), { 'active_tab': 'apie-mus', 'active_item': 'apygarda' }),
    url(r'^apie-mus/long-island-apylinke/$', TemplateView.as_view(template_name='flatpages/li.html'), { 'active_tab': 'apie-mus', 'active_item': 'li' }),
    url(r'^apie-mus/new-york-miesto-apylinke/$', TemplateView.as_view(template_name='flatpages/nyc.html'), { 'active_tab': 'apie-mus', 'active_item': 'nyc' }),
    url(r'^apie-mus/rytinio-long-island-apylinke/$', TemplateView.as_view(template_name='flatpages/rli.html'), { 'active_tab': 'apie-mus', 'active_item': 'rli' }),
    url(r'^apie-mus/rochester-apylinke/$', TemplateView.as_view(template_name='flatpages/rochester.html'), { 'active_tab': 'apie-mus', 'active_item': 'rochester' }),
    url(r'^apie-mus/valstybines-organizacijos/$', TemplateView.as_view(template_name='flatpages/valstybines_organizacijos.html'), { 'active_tab': 'apie-mus', 'active_item': 'valstybines' }),
    url(r'^apie-mus/religines-organizacijos/$', TemplateView.as_view(template_name='flatpages/religines_organizacijos.html'), { 'active_tab': 'apie-mus', 'active_item': 'religines' }),
    url(r'^apie-mus/visuomenines-organizacijos/$', TemplateView.as_view(template_name='flatpages/visuomenines_organizacijos.html'), { 'active_tab': 'apie-mus', 'active_item': 'visuomenines' }),
    url(r'^apie-mus/svietimo-organizacijos/$', TemplateView.as_view(template_name='flatpages/svietimo_organizacijos.html'), { 'active_tab': 'apie-mus', 'active_item': 'svietimo' }),
    url(r'^apie-mus/ziniasklaidos-organizacijos/$', TemplateView.as_view(template_name='flatpages/ziniasklaidos_organizacijos.html'), { 'active_tab': 'apie-mus', 'active_item': 'ziniasklaidos' }),
    url(r'^apie-mus/redakcija/$', TemplateView.as_view(template_name='flatpages/redakcija.html'), { 'active_tab': 'redakcija', 'active_item': 'redakcija' }),
    url(r'^apie-mus/reklama/$', TemplateView.as_view(template_name='flatpages/reklama.html'), { 'active_tab': 'redakcija', 'active_item': 'reklama' }),
    url(r'^apie-mus/pranesk/$', TemplateView.as_view(template_name='flatpages/pranesk.html'), { 'active_tab': 'redakcija', 'active_item': 'pranesk' }),
    url(r'^apie-mus/nuostatos/$', TemplateView.as_view(template_name='flatpages/nuostatos.html'), { 'active_tab': 'redakcija', 'active_item': 'nuostatos' })
)

# Legacy urls
urlpatterns += patterns('',
    url(r'pradzia.html', RedirectView.as_view(url='/')),
    url(r'apie-mus.html', RedirectView.as_view(url='/apie-mus/')),
    url(r'apie-mus/manhattan-apylinke.html', RedirectView.as_view(url='/apie-mus/new-york-miesto-apylinke/')),
    url(r'apie-mus/brooklyn-queens-apylinke.html', RedirectView.as_view(url='/apie-mus/new-york-miesto-apylinke/')),
    url(r'apie-mus/new-york-miesto-apylinke.html', RedirectView.as_view(url='/apie-mus/new-york-miesto-apylinke/')),
    url(r'apie-mus/rytinio-long-island-apylinke.html', RedirectView.as_view(url='/apie-mus/rytinio-long-island-apylinke/')),
    url(r'apie-mus/long-island-apylinke.html', RedirectView.as_view(url='/apie-mus/long-island-apylinke/')),
    url(r'apie-mus/rochester-apylinke.html', RedirectView.as_view(url='/apie-mus/rochester-apylinke/')),
    url(r'apie-mus/portalo-komanda.html', RedirectView.as_view(url='/apie-mus/redakcija/')),
    
    url(r'renginiai.html', RedirectView.as_view(url='/renginiai/')),
    url(r'komentarai.html', RedirectView.as_view(url='/')),
    url(r'straipsniai.html', RedirectView.as_view(url='/straipsniai/')),
    url(r'pranesimai.html', RedirectView.as_view(url='/pranesimai/')),
    url(r'lietuva-apie-mus.html', RedirectView.as_view(url='/straipsniai/')),
    
    url(r'nuotraukos.html', RedirectView.as_view(url='/nuotraukos/')),
    url(r'nuotraukos/2009.html', RedirectView.as_view(url='/nuotraukos/')),
    url(r'nuotraukos/2010.html', RedirectView.as_view(url='/nuotraukos/')),
    url(r'nuotraukos/2011.html', RedirectView.as_view(url='/nuotraukos/')),
    url(r'nuotraukos/2012.html', RedirectView.as_view(url='/nuotraukos/')),
    url(r'nuotraukos/2013-m.html', RedirectView.as_view(url='/nuotraukos/')),
    
    url(r'skelbimai.html', RedirectView.as_view(url='/skelbimai/')),
    url(r'skelbimai/ikelti-skelbima.html', RedirectView.as_view(url='/skelbimai/pateikti/')),
    url(r'skelbimai/skelbimu-sarasas.html', RedirectView.as_view(url='/skelbimai/')),
    
    url(r'login.html', RedirectView.as_view(url='/nariai/prisijungti/')),
    url(r'login/register-user.html', RedirectView.as_view(url='/nariai/registruotis/')),
    url(r'login/saskaita.html', RedirectView.as_view(url='/nariai/prisijungti/')),
)