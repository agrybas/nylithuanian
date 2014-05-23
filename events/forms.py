#encoding=utf-8
import os
from django.contrib.auth.models import User
from django.forms import ModelForm, Textarea, TextInput, ValidationError, Form
from django.forms import EmailField
from django.forms.models import BaseModelFormSet
from models import Event, EventComment, EventAttachment, Venue
from django.forms.models import inlineformset_factory
from django.utils import timezone
from PIL import Image
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives

UPLOAD_IMAGE_SIZE = (300, 200)
# maximum allowed single image size in MB
MAX_IMAGE_SIZE = 5

import logging
from django.conf import settings

if settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)

class EventForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    
class AddEventForm(EventForm):
    
    class Meta:
        model = Event
        widgets = {
            'start_date' : TextInput(attrs={'class' : 'datepicker'}),
            'end_date' : TextInput(attrs={'class' : 'datepicker'}),
            }
        exclude = (
                   'is_approved',
                   )
    
    def save(self):
        event = super(AddEventForm, self).save()
        user = User.objects.get(id = event.user_id)
        
        if not event.is_approved:
            # inform admins about the pending event
            logger.info(u'Sending email about a pending event id={0} edited by user id={1}'.format(event.id, user.id))          
            c = Context({
                         'event' : event,
                         'user' : user
                          })
            subject = u'Naujas renginys laukia patvirtinimo'
            plainText = get_template('emails/new_event.txt').render(c)
            htmlText = get_template('emails/new_event.html').render(c)
            
            msg = EmailMultiAlternatives(subject, plainText, settings.SERVER_EMAIL, to=(settings.EVENTS_PRIMARY_EMAIL,))
            msg.attach_alternative(htmlText, 'text/html')
            msg.send()
            logger.info(u'Email sent successfully.')
            
        else:
            # inform admins about edited existing article
            logger.info(u'Sending email about an edited existing event id={0} edited by user id={1}'.format(event.id, user.id))
            c = Context({ 'event' : event })
            subject = u'Renginys buvo redaguotas'
            plainText = get_template('emails/edited_event.txt').render(c)
            htmlText = get_template('emails/edited_event.html').render(c)

            msg = EmailMultiAlternatives(subject, plainText, settings.SERVER_EMAIL, to=(settings.EVENTS_PRIMARY_EMAIL,))
            msg.attach_alternative(htmlText, 'text/html')
            msg.send()
            logger.info(u'Email sent successfully.')
                    
        return event 
    
    def clean_image(self):
        logger.debug(u'Checking image {0} for side length ratio...'.format(self.cleaned_data['image']))
        image = self.cleaned_data.get('image', False)
        
        if image:
            img = Image.open(image)
            logger.debug(u'Image loaded to memory successfully.')
            if len(image) > MAX_IMAGE_SIZE * 1024 * 1024:
                logger.info(u'Image size too big! Sizes up to {0}MB allowed, uploaded image size is {1}MB. Asking user to upload a smaller image...'.format(MAX_IMAGE_SIZE, len(image)))
                raise ValidationError('Nuotraukos failas per didelis ( > %sMB).' % str(MAX_IMAGE_SIZE))
            logger.debug(u'Image of size {0}KB is allowed. Proceeding...'.format(len(image)/1024))
            target_ratio = float(UPLOAD_IMAGE_SIZE[0])/UPLOAD_IMAGE_SIZE[1]
            logger.debug(u'Target side length ratio: {0}'.format(target_ratio))
            img_ratio = float(img.size[0])/img.size[1]
            logger.debug(u'Actual image side length ratio: {0}'.format(img_ratio))
            
            # if side length ratio is not suitable, request a cropped image
            if (img_ratio != target_ratio): 
                logger.info(u'Uploaded image size is not suitable. Expected width-by-height ratio of {0}, got {1}! Asking user to crop/resize image...'.format(target_ratio, img_ratio))
                raise ValidationError(u'Nuotraukos pločio ir aukščio santykis turi būti 3:2 (pvz., 150px x 100px, 450px x 300px, 900px x 600px, etc.)')
            
            logger.info(u'Uploaded image passed side length ratio test. Proceeding...')
            return image
        else:
            logger.warning("Failed to load user's image file, using a default.")
            return os.path.join('events','images','default.png')
#             raise ValidationError("Nepavyko perskaityti įkeltos nuotraukos failo.")


# EventAttachmentFormSet = inlineformset_factory(Event, EventAttachment, form=AddEventAttachments, can_delete=False)
            
#class EventPreview(FormPreview):
#    form_template = 'events/event_create.html'
#    preview_template = 'events/event_preview.html'
#    
#    def done(self, request, cleaned_data):
#        print cleaned_data
#        reviewed_form = AddEventForm(request.POST, request.FILES)
#        reviewed_form.instance.user = request.user
#        reviewed_form.instance.create_date = reviewed_form.instance.modify_date = timezone.now()
#        reviewed_form.save()
#        return HttpResponseRedirect('../')
    
class AddEventCommentForm(EventForm):
    
    class Meta:
        model = EventComment
        
    def form_valid(self, form):
        form.instance.user = self.request.user.id
        form.instance.create_date = timezone.now()
        return super(AddEventCommentForm, self).form_valid(form)