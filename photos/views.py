from django.conf import settings
from django.views.generic.dates import DateDetailView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic import CreateView, UpdateView
from .models import Photo, Gallery, PhotoComment, BulkPhotoUpload
from .forms import AddPhotoForm, AddGalleryForm, AddPhotoCommentForm, BulkUploadForm
from django.utils import timezone
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
#from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import django

if django.get_version() <= '1.5.5':
    from django.db import connection, transaction
else:
    from django.db import connection

# File-scoped constants

GALLERY_PAGINATE_BY = getattr(settings, 'PHOTO_GALLERY_PAGINATE_BY', 20)  # Number of galleries to display per page.
PHOTO_PAGINATE_BY = getattr(settings, 'PHOTO_PAGINATE_BY', 20)  # Number of photos to display per page.
GALLERY_LATEST_LIMIT = getattr(settings, 'PHOTO_GALLERY_LATEST_LIMIT', 20)  # Number of latest galleries to display

class UserOwnedObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        obj = super(UserOwnedObjectMixin, self).get_object(queryset)
        if self.request.user.is_staff:
            return obj
        if obj.user_id != self.request.user.id:
            raise PermissionDenied
        return obj

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

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date_added = timezone.now()
        return super(GalleryCreateView, self).form_valid(form)
    
class GalleryUpdateView(GalleryView, UpdateView, UserOwnedObjectMixin):
    model = Gallery
    form_class = AddGalleryForm
    template_name = 'photos/gallery_edit.html'
    slug_field = 'id'
    
class GalleryReorderView(GalleryView, UpdateView, UserOwnedObjectMixin):
    model = Gallery
    template_name = 'photos/gallery_reorder.html'
    slug_field = 'id'

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

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date_added = timezone.now()
        return super(PhotoCreateView, self).form_valid(form)
    
class PhotoUpdateView(PhotoView, UpdateView, UserOwnedObjectMixin):
    model = Photo
    form_class = AddPhotoForm
    template_name = 'photos/photo_edit.html'
    slug_field = 'id'
    
class PhotoCommentCreateView(CreateView):
    form_class = AddPhotoCommentForm
    model = PhotoComment
    template_name = 'photo_comments/comment_create.html'
    success_url = '.'
    
    def get_context_data(self, **kwargs):
        kwargs['comment_list'] = PhotoComment.objects.filter(photo=self.kwargs['pk']).order_by('-create_date')
        kwargs['photo'] = Photo.objects.get(id=self.kwargs['pk'])
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(CommentCreateView, self).get_context_data(**kwargs)
    
    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        form.instance.photo_id = self.kwargs['pk']
        form.instance.create_date = timezone.now()
        return super(CommentCreateView, self).form_valid(form)

class BulkPhotoUploadView(CreateView):
    form_class = BulkUploadForm
    model = BulkPhotoUpload
    template_name = 'photos/bulk_upload.html'
#    success_url = '/nuotraukos'
    
    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        return super(BulkPhotoUploadView, self).form_valid(form)
    
@csrf_exempt
@login_required
def sort_photos(request, *args, **kwargs):
    cursor = connection.cursor()
    sql = "UPDATE photos \nSET sort_number = CASE id \n"
    print(sql)
    for index, photo_id in enumerate(request.POST.getlist('photo[]')):
        sql += "WHEN %i THEN %i \n" % (int(str(photo_id)), index)
    sql += " END WHERE id in ({0})".format(",".join(request.POST.getlist('photo[]')))
    cursor.execute(sql)
    if django.get_version() <= '1.5.5':
        transaction.commit_unless_managed() # no longer needed since django v1.6
    return HttpResponse('')