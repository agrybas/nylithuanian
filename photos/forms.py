#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from .models import Photo, Gallery, PhotoComment


class PhotoForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

# TODO Check for too large file size to prevent server DOS
class AddPhotoForm(PhotoForm):
    class Meta:
        model = Photo
        exclude = (
                   'height',
                   'width',
                   'user',
                   'view_count',
                   'crop_from',
                   'date_taken',
                   'date_added',
                   'is_public',
                   )


class AddGalleryForm(PhotoForm):
    class Meta:
        model = Gallery
        exclude = (
                   'user',
                   'date_added',
                   )
        
class AddPhotoCommentForm(PhotoForm):
    class Meta:
        model = PhotoComment

    def form_valid(self, form):
        form.instance.user = self.request.user.id
        form.instance.create_date = timezone.now()
        return super(AddPhotoCommentForm, self).form_valid(form)