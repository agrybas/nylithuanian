#encoding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField
from django.utils import timezone
from django.utils.translation import ugettext as _

COUNTRIES = (
    ('AD', _('Andorra')),
    ('AE', _('United Arab Emirates')),
    ('AF', _('Afghanistan')),
    ('AG', _('Antigua & Barbuda')),
    ('AI', _('Anguilla')),
    ('AL', _('Albania')),
    ('AM', _('Armenia')),
    ('AN', _('Netherlands Antilles')),
    ('AO', _('Angola')),
    ('AQ', _('Antarctica')),
    ('AR', _('Argentina')),
    ('AS', _('American Samoa')),
    ('AT', _('Austria')),
    ('AU', _('Australia')),
    ('AW', _('Aruba')),
    ('AZ', _('Azerbaijan')),
    ('BA', _('Bosnia and Herzegovina')),
    ('BB', _('Barbados')),
    ('BD', _('Bangladesh')),
    ('BE', _('Belgium')),
    ('BF', _('Burkina Faso')),
    ('BG', _('Bulgaria')),
    ('BH', _('Bahrain')),
    ('BI', _('Burundi')),
    ('BJ', _('Benin')),
    ('BM', _('Bermuda')),
    ('BN', _('Brunei Darussalam')),
    ('BO', _('Bolivia')),
    ('BR', _('Brazil')),
    ('BS', _('Bahama')),
    ('BT', _('Bhutan')),
    ('BV', _('Bouvet Island')),
    ('BW', _('Botswana')),
    ('BY', _('Belarus')),
    ('BZ', _('Belize')),
    ('CA', _('Canada')),
    ('CC', _('Cocos (Keeling) Islands')),
    ('CF', _('Central African Republic')),
    ('CG', _('Congo')),
    ('CH', _('Switzerland')),
    ('CI', _('Ivory Coast')),
    ('CK', _('Cook Iislands')),
    ('CL', _('Chile')),
    ('CM', _('Cameroon')),
    ('CN', _('China')),
    ('CO', _('Colombia')),
    ('CR', _('Costa Rica')),
    ('CU', _('Cuba')),
    ('CV', _('Cape Verde')),
    ('CX', _('Christmas Island')),
    ('CY', _('Cyprus')),
    ('CZ', _('Czech Republic')),
    ('DE', _('Germany')),
    ('DJ', _('Djibouti')),
    ('DK', _('Denmark')),
    ('DM', _('Dominica')),
    ('DO', _('Dominican Republic')),
    ('DZ', _('Algeria')),
    ('EC', _('Ecuador')),
    ('EE', _('Estonia')),
    ('EG', _('Egypt')),
    ('EH', _('Western Sahara')),
    ('ER', _('Eritrea')),
    ('ES', _('Spain')),
    ('ET', _('Ethiopia')),
    ('FI', _('Finland')),
    ('FJ', _('Fiji')),
    ('FK', _('Falkland Islands (Malvinas)')),
    ('FM', _('Micronesia')),
    ('FO', _('Faroe Islands')),
    ('FR', _('France')),
    ('FX', _('France, Metropolitan')),
    ('GA', _('Gabon')),
    ('GB', _('United Kingdom (Great Britain)')),
    ('GD', _('Grenada')),
    ('GE', _('Georgia')),
    ('GF', _('French Guiana')),
    ('GH', _('Ghana')),
    ('GI', _('Gibraltar')),
    ('GL', _('Greenland')),
    ('GM', _('Gambia')),
    ('GN', _('Guinea')),
    ('GP', _('Guadeloupe')),
    ('GQ', _('Equatorial Guinea')),
    ('GR', _('Greece')),
    ('GS', _('South Georgia and the South Sandwich Islands')),
    ('GT', _('Guatemala')),
    ('GU', _('Guam')),
    ('GW', _('Guinea-Bissau')),
    ('GY', _('Guyana')),
    ('HK', _('Hong Kong')),
    ('HM', _('Heard & McDonald Islands')),
    ('HN', _('Honduras')),
    ('HR', _('Croatia')),
    ('HT', _('Haiti')),
    ('HU', _('Hungary')),
    ('ID', _('Indonesia')),
    ('IE', _('Ireland')),
    ('IL', _('Israel')),
    ('IN', _('India')),
    ('IO', _('British Indian Ocean Territory')),
    ('IQ', _('Iraq')),
    ('IR', _('Islamic Republic of Iran')),
    ('IS', _('Iceland')),
    ('IT', _('Italy')),
    ('JM', _('Jamaica')),
    ('JO', _('Jordan')),
    ('JP', _('Japan')),
    ('KE', _('Kenya')),
    ('KG', _('Kyrgyzstan')),
    ('KH', _('Cambodia')),
    ('KI', _('Kiribati')),
    ('KM', _('Comoros')),
    ('KN', _('St. Kitts and Nevis')),
    ('KP', _('Korea, Democratic People\'s Republic of')),
    ('KR', _('Korea, Republic of')),
    ('KW', _('Kuwait')),
    ('KY', _('Cayman Islands')),
    ('KZ', _('Kazakhstan')),
    ('LA', _('Lao People\'s Democratic Republic')),
    ('LB', _('Lebanon')),
    ('LC', _('Saint Lucia')),
    ('LI', _('Liechtenstein')),
    ('LK', _('Sri Lanka')),
    ('LR', _('Liberia')),
    ('LS', _('Lesotho')),
    ('LT', _('Lithuania')),
    ('LU', _('Luxembourg')),
    ('LV', _('Latvia')),
    ('LY', _('Libyan Arab Jamahiriya')),
    ('MA', _('Morocco')),
    ('MC', _('Monaco')),
    ('MD', _('Moldova, Republic of')),
    ('MG', _('Madagascar')),
    ('MH', _('Marshall Islands')),
    ('ML', _('Mali')),
    ('MN', _('Mongolia')),
    ('MM', _('Myanmar')),
    ('MO', _('Macau')),
    ('MP', _('Northern Mariana Islands')),
    ('MQ', _('Martinique')),
    ('MR', _('Mauritania')),
    ('MS', _('Monserrat')),
    ('MT', _('Malta')),
    ('MU', _('Mauritius')),
    ('MV', _('Maldives')),
    ('MW', _('Malawi')),
    ('MX', _('Mexico')),
    ('MY', _('Malaysia')),
    ('MZ', _('Mozambique')),
    ('NA', _('Namibia')),
    ('NC', _('New Caledonia')),
    ('NE', _('Niger')),
    ('NF', _('Norfolk Island')),
    ('NG', _('Nigeria')),
    ('NI', _('Nicaragua')),
    ('NL', _('Netherlands')),
    ('NO', _('Norway')),
    ('NP', _('Nepal')),
    ('NR', _('Nauru')),
    ('NU', _('Niue')),
    ('NZ', _('New Zealand')),
    ('OM', _('Oman')),
    ('PA', _('Panama')),
    ('PE', _('Peru')),
    ('PF', _('French Polynesia')),
    ('PG', _('Papua New Guinea')),
    ('PH', _('Philippines')),
    ('PK', _('Pakistan')),
    ('PL', _('Poland')),
    ('PM', _('St. Pierre & Miquelon')),
    ('PN', _('Pitcairn')),
    ('PR', _('Puerto Rico')),
    ('PT', _('Portugal')),
    ('PW', _('Palau')),
    ('PY', _('Paraguay')),
    ('QA', _('Qatar')),
    ('RE', _('Reunion')),
    ('RO', _('Romania')),
    ('RU', _('Russian Federation')),
    ('RW', _('Rwanda')),
    ('SA', _('Saudi Arabia')),
    ('SB', _('Solomon Islands')),
    ('SC', _('Seychelles')),
    ('SD', _('Sudan')),
    ('SE', _('Sweden')),
    ('SG', _('Singapore')),
    ('SH', _('St. Helena')),
    ('SI', _('Slovenia')),
    ('SJ', _('Svalbard & Jan Mayen Islands')),
    ('SK', _('Slovakia')),
    ('SL', _('Sierra Leone')),
    ('SM', _('San Marino')),
    ('SN', _('Senegal')),
    ('SO', _('Somalia')),
    ('SR', _('Suriname')),
    ('ST', _('Sao Tome & Principe')),
    ('SV', _('El Salvador')),
    ('SY', _('Syrian Arab Republic')),
    ('SZ', _('Swaziland')),
    ('TC', _('Turks & Caicos Islands')),
    ('TD', _('Chad')),
    ('TF', _('French Southern Territories')),
    ('TG', _('Togo')),
    ('TH', _('Thailand')),
    ('TJ', _('Tajikistan')),
    ('TK', _('Tokelau')),
    ('TM', _('Turkmenistan')),
    ('TN', _('Tunisia')),
    ('TO', _('Tonga')),
    ('TP', _('East Timor')),
    ('TR', _('Turkey')),
    ('TT', _('Trinidad & Tobago')),
    ('TV', _('Tuvalu')),
    ('TW', _('Taiwan, Province of China')),
    ('TZ', _('Tanzania, United Republic of')),
    ('UA', _('Ukraine')),
    ('UG', _('Uganda')),
    ('UM', _('United States Minor Outlying Islands')),
    ('US', _('United States of America')),
    ('UY', _('Uruguay')),
    ('UZ', _('Uzbekistan')),
    ('VA', _('Vatican City State (Holy See)')),
    ('VC', _('St. Vincent & the Grenadines')),
    ('VE', _('Venezuela')),
    ('VG', _('British Virgin Islands')),
    ('VI', _('United States Virgin Islands')),
    ('VN', _('Viet Nam')),
    ('VU', _('Vanuatu')),
    ('WF', _('Wallis & Futuna Islands')),
    ('WS', _('Samoa')),
    ('YE', _('Yemen')),
    ('YT', _('Mayotte')),
    ('YU', _('Yugoslavia')),
    ('ZA', _('South Africa')),
    ('ZM', _('Zambia')),
    ('ZR', _('Zaire')),
    ('ZW', _('Zimbabwe')),
    ('ZZ', _('Unknown or unspecified country')),
)

class CountryField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 2)
        kwargs.setdefault('choices', COUNTRIES)

        super(CountryField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

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
    phone_number = models.CharField(max_length = 20, verbose_name="Telefono numeris", blank=True)
    email_address = models.EmailField(verbose_name="El. pašto adresas", blank=True)
    start_date = models.DateTimeField(verbose_name='Renginio pradžia', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"')
    end_date = models.DateTimeField(verbose_name='Renginio pabaiga', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"', null = True, blank = True)
    street_address1 = models.CharField(verbose_name="Renginio adresas 1", max_length = 100)
    street_address2 = models.CharField(verbose_name="Renginio adresas 2", max_length = 100, blank = True)
    street_address3 = models.CharField(verbose_name="Renginio adresas 3", max_length = 100, blank = True)
    street_address4 = models.CharField(verbose_name="Renginio adresas 4", max_length = 100, blank = True)
    city = models.CharField(verbose_name="Miestas", max_length = 20, blank = True)
    zip_code = models.CharField(max_length=10, verbose_name="JAV pašto indeksas", blank=True)
    state = USStateField(verbose_name="Valstija", blank = True, null = True)
    country = CountryField(verbose_name="Valstybė", blank=True, null=True)    
    #organizer = models.ForeignKey(Organizer)
    #location = models.ForeignKey(Location)
    image = models.ImageField(max_length=255, verbose_name='Renginio nuotrauka', upload_to='events/images')
    ticket_price = models.DecimalField(verbose_name='Bilietų kaina', max_digits = 5, decimal_places = 2, blank = True, null = True, help_text="Prašome įvesti sumą JAV doleriais; įveskite tik skaičius, pvz., 10.00")
    is_approved = models.BooleanField(null=False, blank=False, default = False) # only approved events will ever be shown publicly; only administrator can change this value
#    publish_date = models.DateTimeField(blank = True, null = True, help_text='Kada renginys turėtų būti publikuotas? Datą įveskite formatu "mm/dd/yyyy hh:mm". Jei norite, kad renginys būtų publikuojamas iškart, palikite laukelį tuščią.') # when a post should be published (shown publicly); null means publish immediately
    create_date = models.DateTimeField(editable= False, default = timezone.now()) # Date when the post was created
    modify_date = models.DateTimeField(editable = False, default = timezone.now()) # Date when the post was last modified
    
    objects = models.Manager()
    approved = ApprovedEventsManager()    
    class Meta:
        db_table = 'events'
        
    def __unicode__(self):
        return self.title
    
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
    