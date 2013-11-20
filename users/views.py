#encoding=utf-8
from django.conf import settings
from django.http import HttpResponseRedirect
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response, get_object_or_404
from users.forms import RegisterUserForm, PromoteUserForm, ChangePasswordForm, EditUserForm, EditUserProfileForm
from django.contrib.auth import logout
from django.contrib.auth.models import User
from users.models import UserProfile, CreateUserError
from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins, EmailMultiAlternatives
from django.views.generic import DetailView
from django.utils import timezone

from articles.models import Article
from events.models import EventReminder

def request_registration(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                plainText = get_template('reg_confirm_email.txt')
                htmlText = get_template('reg_confirm_email.html')
                
                regHash = UserProfile.createUser(data['username'], data['email_address'], data['password'])
                
                # E-mail user to confirm registration
                subject = u'Prašome patvirtinti registraciją'
                c = Context({
                             'username' : data['username'],
                             'registration_hash' : regHash,
                             })
                
                
                msg = EmailMultiAlternatives(subject, plainText.render(c), settings.SERVER_EMAIL, [data['email_address']])
                msg.attach_alternative(htmlText.render(c), 'text/html')
                msg.send()
                return render_to_response('users/register.html', {
                                                           'email_address' : data['email_address'],
                                                           'request_successful' : True,
                                                           }, context_instance=RequestContext(request))

            # errors creating the user
            except CreateUserError as err:
                return render_to_response('users/register.html', {
                                                'form' : form,
                                                'error_message' : err
                                                }, context_instance=RequestContext(request))
        # errors in the form data
        else:
            return render_to_response('users/register.html', {
                                        'form' : form,
                                        }, context_instance=RequestContext(request))
    # initial form load
    else:
        form = RegisterUserForm()
        return render_to_response('users/register.html', {'form' : form},
                                  context_instance=RequestContext(request))

def request_promotion(request):
    if request.method == 'POST':
        form = PromoteUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = UserProfile.objects.get(username=data['username'])
                regHash = user.generateHash()
                currentType = user.getType()               
                            
                # E-mail admins to confirm profile upgrade
                plainText = get_template('promote_user_email.txt')
                subject = u'Keičiamas vartotojo tipas'
                c = Context({
                             'regular_user' : False,
                             'requestor' : request.user.username,
                             'username' : data['username'],
                             'email_address' : data['email_address'],
                             'current_user_type' : currentType,
                             'new_user_type' : data['user_type'],
                             'registration_hash' : regHash
                             })
            
                mail_admins(subject, plainText.render(c))
                return render_to_response('users/promote.html', {
                                                                 'request_successful' : True
                                                                 },context_instance=RequestContext(request))
                
            except:
                return render_to_response('users/promote.html', {
                                                'form' : form,
                                                'request_successful' : False,
                                                'error_message' : 'Klaidos priežastis nežinoma.'
                                                }, context_instance=RequestContext(request))
        else:
            return render_to_response('users/promote.html', {
                                                             'form' : form
                                                             }, context_instance=RequestContext(request))
    else:
        form = PromoteUserForm()
        return render_to_response('users/promote.html', {'form' : form},
                                  context_instance=RequestContext(request))

def confirm_registration(request, username, registrationHash):
    
    user = User.objects.get(username=username)
    userProfile = UserProfile.objects.get(user = user)
    
    if registrationHash == userProfile.getHash():
        user.is_active = True
        user.save()
        userProfile.setType('regular')
        return render_to_response('users/registration_successful.html', {}, context_instance = RequestContext(request))
    else:
        return render_to_response('users/register.html', {
                                    'request_successful' : False,
                                    'error_message' : u'Toks patvirtinimo kodas(' + registrationHash + u') nerastas. Galbūt vartotojo registracija jau patvirtinta?'
                                    }, context_instance = RequestContext(request))
        
def confirm_promotion(request, userType, username, promotionHash):
    user = User.objects.get(username = username)
    userProfile = UserProfile.objects.get(user = user)
    
    if promotionHash == userProfile.getHash():
        userProfile.setType(userType)
        return render_to_response('users/promotion_successful.html', {}, context_instance = RequestContext(request))
    else:
        return render_to_response('users/promote.html',
                                  {
                                   'request_successful' : False,
                                   'error_message' : 'Toks patvirtinimo kodas nerastas. Galbūt vartotojo tipas jau pakeistas?'
                                   }, context_instance = RequestContext(request))

@login_required(login_url='/prisijungti/')
def view_profile(request, username = ""):
    data = {}
    if username == "":
        user = User.objects.get(username = request.user.username)
    else:
        user = User.objects.get(username = username)
    data['username'] = user.username
    data['first_name'] = user.first_name
    data['last_name'] = user.last_name
    data['date_joined'] = user.date_joined
    
    return render_to_response('users/profile.html', {
                             'data' : data, 
                             }, context_instance=RequestContext(request))
    
@login_required(login_url='/prisijungti')
def edit_profile(request):
    if request.method == "POST":
        userForm = EditUserForm(request.POST, instance = request.user)
        userProfileForm = EditUserProfileForm(request.POST, instance = request.user.get_profile())
        if userForm.is_valid() and userProfileForm.is_valid():
            userForm.save()
            userProfileForm.save()
            return HttpResponseRedirect('/mano-saskaita')
        else:
            return render_to_response('users/edit_profile.html', {
                                        'uform' : userForm,
                                        'sform' : userProfileForm,
                                        'edit_failed' : True,
                                        }, context_instance = RequestContext(request))
    else:
        userForm = EditUserForm(instance=request.user)
        userProfileForm = EditUserProfileForm(instance=request.user.get_profile())
        return render_to_response('users/edit_profile.html', {
                                  'uform' : userForm,
                                  'sform' : userProfileForm,
                                  }, context_instance=RequestContext(request))

@login_required(login_url='/prisijungti')
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data['password'] == data['password_verify']:
                request.user.set_password(data['password'])
                request.user.save()

                plainText = get_template('change_password_email.txt')
                htmlText = get_template('change_password_email.html')
                subject = u'Slaptažodis sėkmingai pakeistas'                
                msg = EmailMultiAlternatives(subject, plainText.render(), settings.SERVER_EMAIL, request.user.email)
                msg.attach_alternative(htmlText.render(), 'text/html')
                msg.send()
                                    
                return HttpResponseRedirect('/atsijungti')
            else:
                return render_to_response('users/change_password.html', {
                                      'change_failed' : True,
                                      'error_message' : 'Slaptažodžiai nesutampa.',
                                      }, context_instance=RequestContext(request))
    else:
        form = ChangePasswordForm()
        return render_to_response('users/change_password.html', {
                                                          'form' : form,
                                                          }, context_instance = RequestContext(request))
        
class UserDetailView(DetailView):
    template_name = 'users/user_detail.html'
    slug_field = 'username'
    model = User
    
    def get_context_data(self, **kwargs):
        user = UserProfile.objects.get(user_id=self.request.user.id)
        kwargs['favorite_articles'] = user.favorite_articles.all()
        
        user_articles = Article.objects.filter(user_id=self.request.user.id)
        kwargs['user_articles'] = user_articles
        
        event_reminders = EventReminder.objects.filter(remind_date__gte=timezone.now()).order_by('-remind_date')
        kwargs['event_reminders'] = event_reminders
        
        return super(UserDetailView, self).get_context_data(**kwargs)