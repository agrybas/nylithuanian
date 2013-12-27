#encoding=utf-8
from django import forms
from django.forms import PasswordInput
from users.models import UserProfile
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

class RegisterUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        widgets = {
            'password' : PasswordInput(),
        }
        
    def save(self, commit=True):
        instance = super(RegisterUserForm, self).save(commit)
        user = User.objects.get(username=instance.username)
        user.is_active = False
        user.set_password(self.cleaned_data['password'])
        user.save()
                
        plainText = get_template('emails/reg_confirm_email.txt')
        htmlText = get_template('emails/reg_confirm_email.html')
        
        regHash = UserProfile.createUser(instance.username, instance.email, instance.password)
        
        # E-mail user to confirm registration
        subject = u'Prašome patvirtinti registraciją'
        c = Context({
                     'username' : instance.username,
                     'registration_hash' : regHash,
                     })
        
        msg = EmailMultiAlternatives(subject, plainText.render(c), settings.SERVER_EMAIL, [instance.email])
        msg.attach_alternative(htmlText.render(c), 'text/html')
        msg.send()
        
        return instance

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

class ChangePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Slaptažodis")
    password_verify = forms.CharField(widget=forms.PasswordInput, label="Slaptažodis (pakartoti)")
    
class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('organization_title', 'gender', 'birth_date',
                  'relationship_status', 'home_town', 'home_country', 'shirt_size')
        
class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')