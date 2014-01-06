from django.conf import settings
from django.views.generic.dates import DateDetailView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic import CreateView
from .models import Photo, Gallery
from .forms import AddPhotoForm, AddGalleryForm
from django.utils import timezone

# File-scoped constants

GALLERY_PAGINATE_BY = getattr(settings, 'PHOTO_GALLERY_PAGINATE_BY', 20)  # Number of galleries to display per page.
PHOTO_PAGINATE_BY = getattr(settings, 'PHOTO_PAGINATE_BY', 20)  # Number of photos to display per page.
GALLERY_LATEST_LIMIT = getattr(settings, 'PHOTO_GALLERY_LATEST_LIMIT', 20)  # Number of latest galleries to display

# Gallery views

class GalleryView(object):
    queryset = Gallery.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(GalleryView, self).get_context_data(**kwargs)


class GalleryCreateView(GalleryView, CreateView):
    model = Gallery
    form_class = AddGalleryForm
    template_name = 'photos/gallery_create.html'
#     success_url = '/nuotraukos/gallery'    # CreateView will use Gallery.get_absolute_url() as success_url

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date_added = timezone.now()
        return super(GalleryCreateView, self).form_valid(form)


class GalleryListView(GalleryView, ListView):
    paginate_by = GALLERY_PAGINATE_BY


class GalleryDetailView(GalleryView, DetailView):
    slug_field = 'id'


class GalleryDateDetailView(GalleryView, DateDetailView):
    date_field = 'date_added'
    allow_empty = True
    slug_field = 'id'


# Photo views

class PhotoView(object):
    queryset = Photo.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(PhotoView, self).get_context_data(**kwargs)
    
class PhotoListView(PhotoView, ListView):
    paginate_by = PHOTO_PAGINATE_BY


class PhotoDetailView(PhotoView, DetailView):
    slug_field = 'id'
    

class PhotoDateDetailView(PhotoView, DateDetailView):
    date_field = 'date_added'
    allow_empty = True
    slug_field = 'id'


class PhotoCreateView(CreateView):
    model = Photo
    form_class = AddPhotoForm
    template_name = 'photos/photo_create.html'
#     success_url = '/nuotraukos/gallery'    # CreateView will use Photo.get_absolute_url() as success_url

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date_added = timezone.now()
        return super(PhotoCreateView, self).form_valid(form)
