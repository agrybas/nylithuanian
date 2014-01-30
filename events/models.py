#encoding=utf-8
from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USStateField
from django_countries.fields import CountryField
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.core.validators import RegexValidator

# Reference model containing tags which can be associated with posts or media items
class Tag(models.Model):
    #tag_id = models.PositiveIntegerField(primary_key = True, editable = False)
    title = models.CharField(max_length = 45)
    
    class Meta:
        db_table = 'tags'
        
    def __unicode__(self):
        return self.title
    
# Data model containing locations where events can take place
#class Location(models.Model):
#    #location_id = models.AutoField(primary_key = True, editable = False)
#    title = models.CharField(max_length = 45)
#    street_address1 = models.CharField(max_length = 30)
#    street_address2 = models.CharField(max_length = 30, blank = True)
#    street_address3 = models.CharField(max_length = 30, blank = True)
#    street_address4 = models.CharField(max_length = 30, blank = True)
#    city = models.CharField(max_length = 20)
#    zip_code = USPostalCodeField('US Zip code', blank = True, null = True)
#    state = USStateField('US State', blank = True, null = True)
#    country = models.ForeignKey(Country)
#    
#    def __unicode__(self):
#        return self.title

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
    phone_number = models.CharField(max_length = 20, verbose_name="Telefono numeris", blank=True, validators=[RegexValidator(r'^[-0-9+() ]*$')])
    email_address = models.EmailField(verbose_name="El. pašto adresas", blank=True)
    start_date = models.DateTimeField(verbose_name='Renginio pradžia', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"')
    end_date = models.DateTimeField(verbose_name='Renginio pabaiga', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"', null = True, blank = True)
    street_address1 = models.CharField(verbose_name="Renginio adresas 1", max_length = 100)
    street_address2 = models.CharField(verbose_name="Renginio adresas 2", max_length = 100, blank = True)
    street_address3 = models.CharField(verbose_name="Renginio adresas 3", max_length = 100, blank = True)
    street_address4 = models.CharField(verbose_name="Renginio adresas 4", max_length = 100, blank = True)
    city = models.CharField(verbose_name="Miestas", max_length = 20, blank = True)
    zip_code = models.CharField(max_length=10, verbose_name="Pašto indeksas", blank=True)
    state = USStateField(verbose_name="Valstija", blank = True, null = True)
    country = CountryField(verbose_name='Valstybė', blank=True, null=True)    
    #organizer = models.ForeignKey(Organizer)
    #location = models.ForeignKey(Location)
    image = models.ImageField(max_length=255, verbose_name='Renginio nuotrauka', upload_to='events/images')
#    ticket_price = models.DecimalField(verbose_name='Bilietų kaina', max_digits = 5, decimal_places = 2, blank = True, null = True, help_text="Prašome įvesti sumą JAV doleriais; įveskite tik skaičius, pvz., 10.00")
    is_approved = models.BooleanField(null=False, blank=False, default = False) # only approved events will ever be shown publicly; only administrator can change this value
#    publish_date = models.DateTimeField(blank = True, null = True, help_text='Kada renginys turėtų būti publikuotas? Datą įveskite formatu "mm/dd/yyyy hh:mm". Jei norite, kad renginys būtų publikuojamas iškart, palikite laukelį tuščią.') # when a post should be published (shown publicly); null means publish immediately
    create_date = models.DateTimeField(null=False, blank=False, editable= False, default = timezone.now) # Date when the post was created
    modify_date = models.DateTimeField(null=False, blank=False, editable = False, default = timezone.now) # Date when the post was last modified
    
    objects = models.Manager()
    approved = ApprovedEventsManager()    
    class Meta:
        db_table = 'events'
        
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/renginiai/{0}'.format(self.id)
    
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
    