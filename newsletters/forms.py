#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Newsletter

class NewsletterForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

class AddNewsletterForm(NewsletterForm):   
    class Meta:
        model = Newsletter
        exclude = ('is_approved',)

