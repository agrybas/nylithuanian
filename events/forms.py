#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput, ValidationError
from django.forms.models import BaseModelFormSet
from models import Event, EventComment, EventAttachment
from django.forms.models import inlineformset_factory
#from django.contrib.formtools.preview import FormPreview
from django.contrib.localflavor.us.forms import USZipCodeField
#from django.http import HttpResponseRedirect
from django.utils import timezone
from PIL import Image

UPLOAD_IMAGE_SIZE = (450, 300)

import logging
import nylithuanian.settings

if nylithuanian.settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)

class AddEventForm(ModelForm):
    
    class Meta:
        model = Event
        widgets = {
            'title' : TextInput(),
            'body' : Textarea(),
            'start_date' : TextInput(attrs={'class' : 'datepicker'}),
            'end_date' : TextInput(attrs={'class' : 'datepicker'}),
            }
        exclude = (
                   'is_approved',
                   'publish_date'
                   )
    
    def clean_image(self):
        logger.debug(u'Checking image {0} for side length ratio...'.format(self.cleaned_data['image']))
        img = Image.open(self.cleaned_data['image'])
        logger.debug(u'Image loaded successfully.')
        
        target_ratio = float(UPLOAD_IMAGE_SIZE[0])/UPLOAD_IMAGE_SIZE[1]
        logger.debug(u'Target side length ratio: {0}'.format(target_ratio))
        img_ratio = float(img.size[0])/img.size[1]
        logger.debug(u'Actual image side length ratio: {0}'.format(img_ratio))
        
        # if side length ratio is not suitable, request a cropped image
        if (img_ratio != target_ratio): 
            logger.info(u'Uploaded image size is not suitable. Expected side length ratio of {0}, got {1}! Asking user to crop/resize image...'.format(target_ratio, img_ratio))
            raise ValidationError(u'Image side length ratio must be 3:2.')
        
        logger.info(u'Uploaded image passed side length ratio test. Proceeding...')
        return self.cleaned_data['image']
                
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
    
class AddEventCommentForm(ModelForm):
    
    class Meta:
        model = EventComment
        widgets = {
                   'body' : Textarea(attrs={'cols' : 100, 'rows' : 10}),
                   }
        
    def form_valid(self, form):
        form.instance.user = self.request.user.id
        form.instance.create_date = timezone.now()
        return super(AddEventCommentForm, self).form_valid(form)