#encoding=utf-8
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Textarea, TextInput
from .models import Photo, Gallery, PhotoComment

# maximum allowed single image size in MB
MAX_IMAGE_SIZE = 5

class PhotoForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

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
    
    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > MAX_IMAGE_SIZE * 1024 * 1024:
                raise ValidationError('Nuotraukos failas per didelis ( > %sMB).' % str(MAX_IMAGE_SIZE))
            return image
        else:
            raise ValidationError("Nepavyko perskaityti įkeltos nuotraukos failo.")

class AddGalleryForm(PhotoForm):
    class Meta:
        model = Gallery
        fields = ('title', 'description', 'tags')
        
class AddPhotoCommentForm(PhotoForm):
    class Meta:
        model = PhotoComment

    def form_valid(self, form):
        form.instance.user = self.request.user.id
        form.instance.create_date = timezone.now()
        return super(AddPhotoCommentForm, self).form_valid(form)