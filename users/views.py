#encoding=utf-8
from django.conf import settings
from django.template import RequestContext, Context
from django.contrib.auth import logout
from django.shortcuts import render_to_response
from django.contrib.auth.hashers import make_password
from django.core.mail import mail_admins, EmailMultiAlternatives
from django.views.generic import DetailView, CreateView, ListView, UpdateView
from django.utils import timezone
from django.views.generic.detail import SingleObjectMixin
from django.core.exceptions import PermissionDenied
from django.core.signing import Signer

from .forms import RegisterSiteUserForm, PromoteUserForm, ChangePasswordForm, EditSiteUserForm
from models import CreateUserError, SiteUser
from articles.models import Article
from events.models import EventReminder, Event
from greetings.models import Greeting
from sympathies.models import Sympathy

import random
from django.template.loader import get_template


# def request_registration(request):
#     if request.method == 'POST':
#         form = RegisterUserForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data
#             try:
#                 plainText = get_template('reg_confirm_email.txt')
#                 htmlText = get_template('reg_confirm_email.html')
#                 
#                 regHash = SiteUser.createUser(data['username'], data['email_address'], data['password'])
#                 
#                 # E-mail user to confirm registration
#                 subject = u'Prašome patvirtinti registraciją'
#                 c = Context({
#                              'username' : data['username'],
#                              'registration_hash' : regHash,
#                              })
#                 
#                 
#                 msg = EmailMultiAlternatives(subject, plainText.render(c), settings.SERVER_EMAIL, [data['email_address']])
#                 msg.attach_alternative(htmlText.render(c), 'text/html')
#                 msg.send()
#                 return render_to_response('users/register.html', {
#                                                            'email_address' : data['email_address'],
#                                                            'request_successful' : True,
#                                                            }, context_instance=RequestContext(request))
# 
#             # errors creating the user
#             except CreateUserError as err:
#                 return render_to_response('users/register.html', {
#                                                 'form' : form,
#                                                 'error_message' : err
#                                                 }, context_instance=RequestContext(request))
#         # errors in the form data
#         else:
#             return render_to_response('users/register.html', {
#                                         'form' : form,
#                                         }, context_instance=RequestContext(request))
#     # initial form load
#     else:
#         form = RegisterUserForm()
#         return render_to_response('users/register.html', {'form' : form},
#                                   context_instance=RequestContext(request))

# def request_promotion(request):
#     if request.method == 'POST':
#         form = PromoteUserForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data
#             try:
#                 user = SiteUser.objects.get(username=data['username'])
#                 regHash = user.generateHash()
#                 currentType = user.getType()               
#                             
#                 # E-mail admins to confirm profile upgrade
#                 plainText = get_template('promote_user_email.txt')
#                 subject = u'Keičiamas vartotojo tipas'
#                 c = Context({
#                              'regular_user' : False,
#                              'requestor' : request.user.username,
#                              'username' : data['username'],
#                              'email_address' : data['email_address'],
#                              'current_user_type' : currentType,
#                              'new_user_type' : data['user_type'],
#                              'registration_hash' : regHash
#                              })
#             
#                 mail_admins(subject, plainText.render(c))
#                 return render_to_response('users/promote.html', {
#                                                                  'request_successful' : True
#                                                                  },context_instance=RequestContext(request))
#                 
#             except:
#                 return render_to_response('users/promote.html', {
#                                                 'form' : form,
#                                                 'request_successful' : False,
#                                                 'error_message' : 'Klaidos priežastis nežinoma.'
#                                                 }, context_instance=RequestContext(request))
#         else:
#             return render_to_response('users/promote.html', {
#                                                              'form' : form
#                                                              }, context_instance=RequestContext(request))
#     else:
#         form = PromoteUserForm()
#         return render_to_response('users/promote.html', {'form' : form},
#                                   context_instance=RequestContext(request))

def confirm_registration(request, username, registrationHash):
    
    user = SiteUser.objects.get(username = username)
    
    if registrationHash == user.getHash():
        user.is_active = True
        user.save()
        return render_to_response('users/registration_successful.html', {}, context_instance = RequestContext(request))
    else:
        return render_to_response('users/register.html', {
                                    'request_successful' : False,
                                    'error_message' : u'Toks patvirtinimo kodas(' + registrationHash + u') nerastas. Galbūt vartotojo registracija jau patvirtinta?'
                                    }, context_instance = RequestContext(request))
        
# def confirm_promotion(request, userType, username, promotionHash):
#     user = User.objects.get(username = username)
#     siteUser = siteUser.objects.get(user = user)
#     
#     if promotionHash == siteUser.getHash():
#         siteUser.setType(userType)
#         return render_to_response('users/promotion_successful.html', {}, context_instance = RequestContext(request))
#     else:
#         return render_to_response('users/promote.html',
#                                   {
#                                    'request_successful' : False,
#                                    'error_message' : 'Toks patvirtinimo kodas nerastas. Galbūt vartotojo tipas jau pakeistas?'
#                                    }, context_instance = RequestContext(request))

# @login_required(login_url='/prisijungti/')
# def view_profile(request, username = ""):
#     data = {}
#     if username == "":
#         user = User.objects.get(username = request.user.username)
#     else:
#         user = User.objects.get(username = username)
#     data['username'] = user.username
#     data['first_name'] = user.first_name
#     data['last_name'] = user.last_name
#     data['date_joined'] = user.date_joined
#     
#     return render_to_response('users/profile.html', {
#                              'data' : data, 
#                              }, context_instance=RequestContext(request))
    
# @login_required(login_url='/prisijungti')
# def edit_profile(request):
#     if request.method == "POST":
#         userForm = EditUserForm(request.POST, instance = request.user)
#         siteUserForm = EditSiteUserForm(request.POST, instance = request.user.get_profile())
#         if userForm.is_valid() and siteUserForm.is_valid():
#             userForm.save()
#             siteUserForm.save()
#             return HttpResponseRedirect('/mano-saskaita')
#         else:
#             return render_to_response('users/edit_profile.html', {
#                                         'uform' : userForm,
#                                         'sform' : siteUserForm,
#                                         'edit_failed' : True,
#                                         }, context_instance = RequestContext(request))
#     else:
#         userForm = EditUserForm(instance=request.user)
#         siteUserForm = EditSiteUserForm(instance=request.user.get_profile())
#         return render_to_response('users/edit_profile.html', {
#                                   'uform' : userForm,
#                                   'sform' : siteUserForm,
#                                   }, context_instance=RequestContext(request))

# @login_required(login_url='/prisijungti')
# def change_password(request):
#     if request.method == "POST":
#         form = ChangePasswordForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data
#             if data['password'] == data['password_verify']:
#                 request.user.set_password(data['password'])
#                 request.user.save()
# 
#                 plainText = get_template('change_password_email.txt')
#                 htmlText = get_template('change_password_email.html')
#                 subject = u'Slaptažodis sėkmingai pakeistas'                
#                 msg = EmailMultiAlternatives(subject, plainText.render(), settings.SERVER_EMAIL, request.user.email)
#                 msg.attach_alternative(htmlText.render(), 'text/html')
#                 msg.send()
#                                     
#                 return HttpResponseRedirect('/atsijungti')
#             else:
#                 return render_to_response('users/change_password.html', {
#                                       'change_failed' : True,
#                                       'error_message' : 'Slaptažodžiai nesutampa.',
#                                       }, context_instance=RequestContext(request))
#     else:
#         form = ChangePasswordForm()
#         return render_to_response('users/change_password.html', {
#                                                           'form' : form,
#                                                           }, context_instance = RequestContext(request))

# TODO Add password strength meter
# TODO Prevent simple passwords (use a dictionary of common passwords) -- https://wiki.skullsecurity.org/Passwords        
class SiteUserCreateView(CreateView):                                               
    template_name = 'users/siteuser_create.html'
    form_class = RegisterSiteUserForm
    model = SiteUser
    success_url = '/nariai/registruotis/priimta'

    def form_valid(self, form):
        form.instance.is_active = False
        form.instance.date_joined = timezone.now()
        form.instance.password = make_password(form.instance.password)
#        signer = Signer(salt=form.instance.date_joined.strftime("%Y-%m-%d %H:%i:%s") + str(random.randint(1, 100)))
        form.instance.temp_hash = Signer(salt=form.instance.date_joined.strftime("%Y-%m-%d %H:%i:%s") + str(random.randint(1, 100))).signature(form.instance.username)    # registration confirmation hash

        # E-mail user to confirm registration
        plainText = get_template('emails/reg_confirm_email.txt')
        htmlText = get_template('emails/reg_confirm_email.html')
        subject = u'Prašome patvirtinti registraciją'
        c = Context({
                     'username' : form.instance.username,
                     'registration_hash' : form.instance.temp_hash,
                     })
        
        
        msg = EmailMultiAlternatives(subject, plainText.render(c), settings.SERVER_EMAIL, (form.instance.email, ))
        msg.attach_alternative(htmlText.render(c), 'text/html')
        msg.send()

        return super(SiteUserCreateView, self).form_valid(form)


class SiteUserDetailView(DetailView):
    model = SiteUser
    slug_field = 'username'
    
    def get_template_names(self):
        if self.kwargs['slug'] == self.request.user.username:
            return 'users/user_profile.html'
        return 'users/user_detail.html'
    
    def get_context_data(self, **kwargs):
        if self.kwargs['slug'] == self.request.user.username:
            kwargs['favorite_articles'] = SiteUser.objects.get(id=self.request.user.id).favorite_articles.all()
            kwargs['user_articles'] = Article.objects.filter(id=self.request.user.id)
            kwargs['event_reminders'] = EventReminder.objects.filter(remind_date__gte=timezone.now()).order_by('-remind_date')
            kwargs['user_events'] = Event.objects.filter(user_id=self.request.user.id).order_by('-modify_date')[:5]
            kwargs['user_greetings'] = Greeting.objects.filter(user=self.request.user).order_by('-modify_date')[:5]
            kwargs['user_sympathies'] = Sympathy.objects.filter(user=self.request.user).order_by('-modify_date')[:5]
        return super(SiteUserDetailView, self).get_context_data(**kwargs)
    
class UserOwnedObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        obj = super(UserOwnedObjectMixin, self).get_object(queryset)
        if self.request.user.is_staff:
            return obj
        if obj.id != self.request.user.id:
            raise PermissionDenied
        return obj
    
class SiteUserUpdateView(UpdateView, UserOwnedObjectMixin):
    model = SiteUser
    slug_field = 'username'
    form_class = EditSiteUserForm
    template_name = 'users/siteuser_edit.html'
    success_url = '/nariai'
    