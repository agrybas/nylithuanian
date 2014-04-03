#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Announcement

class AnnouncementForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

class AddAnnouncementForm(AnnouncementForm):   
    class Meta:
        model = Announcement
        exclude = ('is_approved',)

