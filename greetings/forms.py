#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Greeting, GreetingComment

class AddGreetingForm(ModelForm):
    error_css_class = 'error'
    class Meta:
        model = Greeting
        exclude = ('is_approved',)
    
class AddGreetingCommentForm(ModelForm):
    class Meta:
        model = GreetingComment
