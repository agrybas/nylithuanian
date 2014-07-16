#encoding=utf-8
from django import forms
from django.forms import PasswordInput, RadioSelect
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.forms import PasswordChangeForm

from .models import SiteUser
from .validators import *

class RegisterSiteUserForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    password = forms.CharField(
                               label='Slaptažodis',
                               max_length=128,
                               help_text='Slaptažodis turi būti mažiausiai 8 simbolių.',
                               widget=PasswordInput,
                               validators=[
                                           MinLengthValidator(8),
                                           validate_uncommon_word,
                                           ]
                               )
    confirm_password = forms.CharField(label='Slaptažodis (pakartoti)', max_length=128, widget=PasswordInput)
    email = forms.EmailField(label='El. pašto adresas', required=True)
    
    class Meta:
        model = SiteUser
        fields = ('username', 'password', 'confirm_password', 'email')
        
    def clean(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')
        if password1 and password1 != password2:
            raise ValidationError(u'Įvestos slaptažodžių reikšmės nesutampa.')
        return super(RegisterSiteUserForm, self).clean()
    
    def save(self):
        
        siteUser = super(RegisterSiteUserForm, self).save()
        
        # E-mail user to confirm registration
        plainText = get_template('emails/reg_confirm_email.txt')
        htmlText = get_template('emails/reg_confirm_email.html')
        subject = u'Prašome patvirtinti registraciją'
        c = Context({
                     'username' : siteUser.username,
                     'registration_hash' : siteUser.temp_hash,
                     'SITE_URL': settings.SITE_URL,
                     })
        
        
        msg = EmailMultiAlternatives(subject, plainText.render(c), settings.SERVER_EMAIL, (siteUser.email, ))
        msg.attach_alternative(htmlText.render(c), 'text/html')
        msg.send()
        
        return siteUser
    

class SiteUserPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(
                               label='Slaptažodis',
                               max_length=128,
                               help_text='Slaptažodis turi būti mažiausiai 8 simbolių.',
                               widget=PasswordInput,
                               validators=[
                                           MinLengthValidator(8),
                                           validate_uncommon_word,
                                           ]
                               )

class PromoteUserForm(forms.Form):
    USER_TYPES = (
                  ('regular', 'Regular User'),
                  ('admin', 'Administrator'),
                  ('staff', 'Staff Member'),
                  ('photographer', 'Photographer'),
                  ('journalist', 'Journalist'),
                  )
    username = forms.CharField(max_length = 30, label='Vartotojo vardas')
    user_type = forms.ChoiceField(choices = USER_TYPES, label='Vartotojo tipas')
  
class EditSiteUserForm(forms.ModelForm):
    class Meta:
        model = SiteUser
        widgets = {
                   'is_subscribed': RadioSelect(),
                   }
        exclude = ('username', 'password', 'email', 'last_login', 'date_joined', 'is_superuser', 'is_active', 'is_staff')
        