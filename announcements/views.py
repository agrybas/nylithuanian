#encoding=utf-8
import logging
import nylithuanian.settings
from django.contrib.syndication.views import Feed
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.formtools.preview import FormPreview
from django.template.loader import get_template
from .models import Announcement
from .forms import AddAnnouncementForm
from django.template import Context, RequestContext
from django.core.mail import mail_admins
from django.shortcuts import render_to_response

if nylithuanian.settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)


class AnnouncementListView(ListView):
    model = Announcement
    paginate_by = 10
    queryset = Announcement.public.order_by('-create_date')
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(AnnouncementListView, self).get_context_data(**kwargs)

class AnnouncementDetailView(DetailView):
    model = Announcement
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(AnnouncementDetailView, self).get_context_data(**kwargs)
    
class AnnouncementRssView(Feed):
    title = 'Naujausi pranešimai Niujorko lietuviams'
    link = '/pranesimai/'
    description = 'Naujausi pranešimai Niujorko lietuviams svarbiomis temomis.'
    
    def items(self):
        return Announcement.public.order_by('-create_date')

    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        if len(item.body) <= 1000:
            return item.body
        return item.body[:1000].rsplit(' ', 1)[0] + '...'
        

class UserOwnedObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        obj = super(UserOwnedObjectMixin, self).get_object(queryset)
        if self.request.user.is_staff:
            return obj
        if obj.user_id != self.request.user.id:
            raise PermissionDenied
        return obj


class AnnouncementUpdateView(UpdateView, UserOwnedObjectMixin):
    model = Announcement
    form_class = AddAnnouncementForm
    success_url = '../'
    template_name = 'announcements/announcement_edit.html'
    
    @method_decorator(login_required(login_url='/nariai/prisijungti'))
    #@method_decorator(user_passes_test(lambda u: u.is_staff, login_url='/stop'))
    def dispatch(self, *args, **kwargs):
        return super(AnnouncementUpdateView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        kwargs['form'] = AddAnnouncementForm(instance=Announcement.objects.get(id=self.kwargs['pk']))
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(AnnouncementUpdateView, self).get_context_data(**kwargs)
    
class AddAnnouncementPreview(FormPreview):
    form_template = 'announcements/announcement_create.html'
    preview_template = 'announcements/announcement_preview.html'
      
    @method_decorator(login_required(login_url='/nariai/prisijungti'))
    def done(self, request, cleaned_data):
        try:
            logger.info(u'Adding a new announcement "{0}" to database...'.format(cleaned_data['title']))
            
            reviewed_form = AddAnnouncementForm(cleaned_data)
            logger.debug(u'title: {0}'.format(cleaned_data['title']))
            logger.debug(u'body: {0}'.format(cleaned_data['body'][:50]))
            logger.debug(u'first_name: {0}'.format(cleaned_data['first_name']))
            logger.debug(u'last_name: {0}'.format(cleaned_data['last_name']))
            logger.debug(u'organization_title: {0}'.format(cleaned_data['organization_title']))
            logger.debug(u'phone: {0}'.format(cleaned_data['phone_number']))
            logger.debug(u'email: {0}'.format(cleaned_data['email_address']))
            logger.debug(u'signature: {0}'.format(cleaned_data['signature']))
            
            reviewed_form.instance.user = request.user
            logger.debug(u'User ID: {0}'.format(reviewed_form.instance.user.id))
            
            # already provided as default values in model definition
            #reviewed_form.instance.create_date = reviewed_form.instance.modify_date = timezone.now()
            #logger.debug(u'Date created: {0}'.format(reviewed_form.instance.create_date))
            #logger.debug(u'Date modified: {0}'.format(reviewed_form.instance.modify_date))
            
            reviewed_form.save()
            logger.info(u'Announcement has been added successfully.')
            
            # inform admins about the pending Announcement
            plainText = get_template('emails/new_announcement.txt')
            htmlText = get_template('emails/new_announcement.html')
            subject = u'Naujas pranešimas'
            c = Context({
                     'announcement' : cleaned_data,
                     })
        
            mail_admins(subject=subject, message=plainText.render(c), html_message=htmlText.render(c))
            
            
            return render_to_response('announcements/success.html', {
                                        'message' : 'Ačiū! Jūsų pranešimas buvo sėkmingai pateiktas. Svetainės administratoriai artimiausiu metu perskaitys Jūsų straipsnį ir nedelsiant paskelbs jį svetainėje. Jei kiltų neaiškumų, susisieksime su Jumis tiesiogiai.',
                                        }, context_instance=RequestContext(request))
        except:
            logger.exception('Exception thrown while adding a new announcement:')