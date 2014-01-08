#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Greeting, GreetingComment

class GreetingForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

class AddGreetingForm(GreetingForm):
    
    class Meta:
        model = Greeting
        exclude = ('is_approved',)
    
class AddGreetingCommentForm(GreetingForm):
    class Meta:
        model = GreetingComment
