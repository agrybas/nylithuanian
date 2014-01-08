#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Sympathy, SympathyComment

class SympathyForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

class AddSympathyForm(SympathyForm):
    error_css_class = 'error'
    class Meta:
        model = Sympathy
        exclude = ('is_approved',)
    
class AddSympathyCommentForm(SympathyForm):
    class Meta:
        model = SympathyComment
