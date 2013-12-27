#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Sympathy, SympathyComment

class AddSympathyForm(ModelForm):
    error_css_class = 'error'
    class Meta:
        model = Sympathy
        exclude = ('is_approved',)
    
class AddSympathyCommentForm(ModelForm):
    class Meta:
        model = SympathyComment
