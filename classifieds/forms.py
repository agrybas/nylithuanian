#encoding=utf-8
from models import Classified
from django.forms import ModelForm

class AddClassifiedForm(ModelForm):   
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Classified
        exclude = ('is_approved', )