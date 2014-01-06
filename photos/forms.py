#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from .models import Photo, Gallery


class AddPhotoForm(ModelForm):
    class Meta:
        model = Photo
        widgets = {
            'title': TextInput(),
            'description': Textarea(),
        }
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


class AddGalleryForm(ModelForm):
    class Meta:
        model = Gallery
        widgets = {
            'title': TextInput(attrs={'size': 100}),
            'description': Textarea(attrs={'cols': 100, 'rows': 5})
        }
        exclude = (
            'user',
            'date_added',
        )