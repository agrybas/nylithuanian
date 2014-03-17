#encoding=utf-8
from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USStateField
from django_countries.fields import CountryField
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_text
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# Reference model containing tags which can be associated with posts or media items
class Tag(models.Model):
    #tag_id = models.PositiveIntegerField(primary_key = True, editable = False)
    title = models.CharField(max_length = 45)
    
    class Meta:
        db_table = 'tags'
        
    def __unicode__(self):
        return self.title
    
# Data model containing locations where events can take place
class Venue(models.Model):
    title = models.CharField(max_length = 255)
    street_address1 = models.CharField(verbose_name="Adresas 1", max_length = 100)
    street_address2 = models.CharField(verbose_name="Adresas 2", max_length = 100, blank = True)
    street_address3 = models.CharField(verbose_name="Adresas 3", max_length = 100, blank = True)
    city = models.CharField(verbose_name="Miestas", max_length = 20, blank = True)
    zip_code = models.CharField(max_length=10, verbose_name="Pašto indeksas", blank=True)
    state = USStateField(verbose_name="Valstija", blank = True, null = True)
    country = CountryField(verbose_name='Šalis', blank=True, null=True)    
    
    def __unicode__(self):
        return self.title

class ApprovedEventsManager(models.Manager):
    def get_query_set(self):
        return super(ApprovedEventsManager, self).get_query_set().filter(is_approved=True)

# Data model for events; an event must have an organizer and a location specified; an event must be approved by administrator before
# it's shown publicly; contact information is shown that of an organizer, not of the user who created the event entry;
# a user can select an organizer from a list of those associated with the user's account
class Event(models.Model):
    title = models.CharField(max_length=100, verbose_name='Renginio pavadinimas')
    body = models.TextField(verbose_name="Renginio aprašymas", help_text='Tekstas turi būti rašomas naudojant <a target="_blank" href="http://en.wikipedia.org/wiki/Textile_%28markup_language%29">Textile</a> žymėjimo kalbą.')
    user = models.ForeignKey(User, editable=False) # user who created the post; only that user can edit or delete it
    first_name = models.CharField(max_length=30, blank=True, verbose_name="Vardas")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="Pavardė")
    organization_title = models.CharField(max_length=100, blank=True, verbose_name="Organizacijos pavadinimas")
    phone_number = models.CharField(max_length = 20, verbose_name="Telefono numeris", blank=True, validators=[RegexValidator(r'^[-0-9+() ]*$', message=u'Telefono numeris turi būti sudarytas tik iš skaičių, tarpų ir simbolių -,+,(,).')])
    email_address = models.EmailField(verbose_name="El. pašto adresas", blank=True)
    start_date = models.DateTimeField(verbose_name='Renginio pradžia', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"')
    end_date = models.DateTimeField(verbose_name='Renginio pabaiga', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"', null = True, blank = True)
    address_title = models.CharField(max_length = 255, verbose_name='Vietos pavadinimas')
    street_address1 = models.CharField(verbose_name="Adresas 1", max_length = 100)
    street_address2 = models.CharField(verbose_name="Adresas 2", max_length = 100, blank = True)
    street_address3 = models.CharField(verbose_name="Adresas 3", max_length = 100, blank = True)
    city = models.CharField(verbose_name="Miestas", max_length = 20, blank = True)
    zip_code = models.CharField(max_length=10, verbose_name="Pašto indeksas", blank=True)
    state = USStateField(verbose_name="Valstija", blank = True, null = True)
    country = CountryField(verbose_name='Šalis', blank=True, null=True)    
    image = models.ImageField(max_length=255, verbose_name='Renginio nuotrauka', upload_to='events/images')
    is_community_event = models.BooleanField(verbose_name="Niujorko apygardos arba apylinkės renginys", help_text="Pažymėkite, jei renginį organizuoja JAV LB Niujorko apygarda arba viena iš Niujorko apygardai priklausančių apylinkių.", null=False, blank=False, default=False)
    is_approved = models.BooleanField(null=False, blank=False, default = False) # only approved events will ever be shown publicly; only administrator can change this value
    create_date = models.DateTimeField(null=False, blank=False, editable= False, default = timezone.now) # Date when the post was created
    modify_date = models.DateTimeField(null=False, blank=False, editable = False, default = timezone.now) # Date when the post was last modified
    version_number = models.PositiveSmallIntegerField(null=False, blank=False, editable=False, default=1) # keeps track of changes made to object; increased if start_date or end_date is changed (used in ICS calendar generation) 
    
    objects = models.Manager()
    approved = ApprovedEventsManager()    
    class Meta:
        db_table = 'events'
        ordering = ['start_date', ]
        
    def __unicode__(self):
        if self.start_date:
            return u'{0} {1}'.format(self.start_date.strftime('%Y-%m-%d'), self.title)
        else:
            return self.title

    def get_absolute_url(self):
        return '/renginiai/{0}'.format(self.id)
    
    def get_full_address(self):
        full_address = self.address_title
        if self.street_address1:
            full_address += u", {0}".format(self.street_address1)
        if self.street_address2:
            full_address += u", {0}".format(self.street_address2)
        if self.street_address3:
            full_address += u", {0}".format(self.street_address3)
        if self.city:
            full_address += u", {0}".format(self.city)
        if self.state:
            full_address += u", {0}".format(self.state)
        if self.zip_code:
            full_address += u" {0}".format(self.zip_code)
        if self.country:
            full_address += u", {0}".format(self.country)
        return full_address
    
    def get_organizer_full_name(self):
        if self.first_name:
            full_name = self.first_name
            if self.last_name:
                full_name += u" {0}".format(self.last_name)
            if self.organization_title:
                full_name += u", {0}".format(self.organization_title)
            return full_name
        elif self.organization_title:
            return self.organization_title
        return ''
    
    @property
    def next_event_exists(self):
        return Event.approved.filter(start_date__gt=self.start_date).exists()
    
    @property
    def previous_event_exists(self):
        return Event.approved.filter(start_date__lt=self.start_date).exists()
    
    @property
    def get_next_event_url(self):
        try:
            next_event = Event.approved.filter(start_date__gt=self.start_date)[0]
            return next_event.get_absolute_url()
        except Event.DoesNotExist:
            return None    
    
    @property
    def get_previous_event_url(self):
        try:
            previous_event = Event.approved.filter(start_date__lt=self.start_date)
            previous_event = previous_event[len(previous_event) - 1]
            return previous_event.get_absolute_url()    
        except Event.DoesNotExist:
            return None
        
    @property
    def get_next_event_title(self):
        try:
            next_event = Event.approved.filter(start_date__gt=self.start_date)[0]
            return next_event.title
        except Event.DoesNotExist:
            return None    

    @property
    def get_previous_event_title(self):
        try:
            previous_event = Event.approved.filter(start_date__lt=self.start_date)
            previous_event = previous_event[len(previous_event) - 1]
            return previous_event.title    
        except Event.DoesNotExist:
            return None

        
class EventAttachment(models.Model):
    event = models.ForeignKey(Event, editable=False) # event the attachment is associated with
    file = models.FileField(verbose_name='Prisegamas dokumentas', upload_to='events/attachments', blank=True)
    title = models.CharField(max_length=100, verbose_name='Dokumento pavadinimas', blank=True)
    description = models.CharField(max_length=255, verbose_name='Dokumento aprašymas', blank=True)
    upload_date = models.DateTimeField(editable=False) # date & time when the document was uploaded
    
    class Meta:
        db_table = 'event_attachments'
        
    def __unicode__(self):
        return self.title + '(' + file + ')'
    
class EventComment(models.Model):
    user = models.ForeignKey(User, editable=False) # user who created the post; only that user can edit or delete it
    event = models.ForeignKey(Event, editable = False)
    body = models.TextField(verbose_name='Komentaras')
    create_date = models.DateTimeField('Date when the post was created', editable= False, default = timezone.now())

    class Meta:
        db_table = 'event_comments'
        
    def __unicode__(self):
        return self.user.username + ': ' + self.body[:50]
    
class EventReminder(models.Model):
    class Meta:
        db_table = 'event_reminders'
        
    user = models.ForeignKey(User, blank=False, null=False, editable=False, verbose_name='Vartotojas, užsisakęs priminimą') # user who requested the reminder
    event = models.ForeignKey(Event, blank=False, null=False, verbose_name='Renginys, apie kurį pageidaujama priminti')
    remind_date = models.DateTimeField(blank=False, null=False, verbose_name='Priminimo data ir laikas')
    task_id = models.CharField(max_length=256, blank=True, null=True, verbose_name='Išsaugotos užduoties ID') # celery task ID
    