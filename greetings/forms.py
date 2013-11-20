#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Greeting, GreetingComment

class AddGreetingForm(ModelForm):
    error_css_class = 'error'
    class Meta:
        model = Greeting
        widgets = {
            'title' : TextInput(attrs={'size' : 100}),
            'body' : Textarea(attrs={'cols' : 100, 'rows' : 20}),
        }
        exclude = ('is_approved',)
    
class AddGreetingCommentForm(ModelForm):
    class Meta:
        model = GreetingComment
        widgets = {
                   'body' : Textarea(attrs={'cols' : 100, 'rows' : 10}),
                   }
