#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Sympathy, SympathyComment

class AddSympathyForm(ModelForm):
    error_css_class = 'error'
    class Meta:
        model = Sympathy
        widgets = {
            'title' : TextInput(attrs={'size' : 100}),
            'body' : Textarea(attrs={'cols' : 100, 'rows' : 20}),
        }
        exclude = ('is_approved',)
    
class AddSympathyCommentForm(ModelForm):
    class Meta:
        model = SympathyComment
        widgets = {
                   'body' : Textarea(attrs={'cols' : 100, 'rows' : 10}),
                   }
