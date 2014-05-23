#encoding=utf-8
from django.conf.urls import patterns, url
from django.views.generic import ListView
from views import ArticleCommentCreateView,  ArticleDetailView,  AddArticlePreview, ArticleUpdateView, ArticleListView, ArticleRssView
from views import toggle_favorite, approve
from forms import AddArticleForm
from models import Article
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^$',
        ArticleListView.as_view()
        ),
                       
    url(r'^rss/$', ArticleRssView()),
                       
    url(r'^pateikti/$',
        login_required(login_url='/nariai/prisijungti')(AddArticlePreview(AddArticleForm))
        ),
                       
    #url(r'^archyvas/$', PastEventsListView.as_view()),
    
    url(r'^(?P<pk>\d+)/$',
        ArticleDetailView.as_view()
        ),
    
    url(r'^(?P<pk>\d+)/patvirtinti/$', approve),
                       
    url(r'^(?P<pk>\d+)/redaguoti/$',
        ArticleUpdateView.as_view(),
        ),
                       
    #url(r'^(?P<pk>\d+)/redaguoti/$', ArticleUpdateView.as_view()),
    
    url(r'^(?P<pk>\d+)/komentarai/$',
        ArticleCommentCreateView.as_view()
        ),
                       
    url(r'^(?P<pk>\d+)/pazymeti/$', login_required(login_url='/nariai/prisijungti')(toggle_favorite)),
)
