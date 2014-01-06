from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import PhotoCreateView, PhotoListView, PhotoDetailView, GalleryCreateView, GalleryListView, GalleryDetailView, PhotoDateDetailView, GalleryDateDetailView


urlpatterns = patterns('',
                       url(r'^gallery/$', GalleryListView.as_view()),
                       url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$', GalleryDateDetailView.as_view(), name='pl-gallery-detail'),
                       url(r'^gallery/pateikti/$', login_required(login_url='/nariai/prisijungti')(GalleryCreateView.as_view()), name='add-gallery'),
                       url(r'^gallery/page/(?P<page>[0-9]+)/$', GalleryListView.as_view(), name='pl-gallery-list'),
                        url(r'^gallery/(?P<slug>[\-\d\w]+)/$', GalleryDetailView.as_view(), name='pl-gallery'),
                        url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
                            PhotoDateDetailView.as_view(), name='pl-photo-detail'),
                        url(r'^photo/page/(?P<page>[0-9]+)/$', PhotoListView.as_view(), name='pl-photo-list'),
                        url(r'^photo/pateikti/$',
                            login_required(login_url='/nariai/prisijungti')(PhotoCreateView.as_view()),
                            name='add-photo'),
                        # url(r'^photo/pateikti-daug/$',
                        #     login_required(login_url='/nariai/prisijungti')(CreateView.as_view(model=GalleryUpload)),
                        #     name='add-galleryupload'),
                        url(r'^photo/(?P<slug>[\-\d\w]+)/$', PhotoDetailView.as_view(), name='pl-photo'),
                       )


# url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', GalleryDayArchiveView.as_view(), name='pl-gallery-archive-day'),
# url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', GalleryMonthArchiveView.as_view(), name='pl-gallery-archive-month'),
# url(r'^gallery/(?P<year>\d{4})/$', GalleryYearArchiveView.as_view(), name='pl-gallery-archive-year'),
# url(r'^photo/$', PhotoArchiveIndexView.as_view(), name='pl-photo-archive'),
# url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', PhotoDayArchiveView.as_view(), name='pl-photo-archive-day'),
# url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', PhotoMonthArchiveView.as_view(), name='pl-photo-archive-month'),
# url(r'^photo/(?P<year>\d{4})/$', PhotoYearArchiveView.as_view(), name='pl-photo-archive-year'),
