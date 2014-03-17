#encoding=utf-8
import os
from django.forms import ModelForm, Textarea, TextInput, ValidationError, Form
from django.forms import EmailField
from django.forms.models import BaseModelFormSet
from models import Event, EventComment, EventAttachment, Venue
from django.forms.models import inlineformset_factory
from django.utils import timezone
from PIL import Image

UPLOAD_IMAGE_SIZE = (300, 200)
# maximum allowed single image size in MB
MAX_IMAGE_SIZE = 5

import logging
import nylithuanian.settings

if nylithuanian.settings.DEBUG:
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
                   'publish_date'
                   )
    
    def clean_image(self):
        logger.debug(u'Checking image {0} for side length ratio...'.format(self.cleaned_data['image']))
        image = self.cleaned_data.get('image', False)
        img = Image.open(image)
        
        if image:
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
            raise ValidationError("Nepavyko perskaityti įkeltos nuotraukos failo.")


class SendEmailForm(Form):
    email = EmailField(label="El. pašto adresas", help_text="Įveskite el. pašto adresą, kuriuo norėtumėte gauti naujienlaiškį.")

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