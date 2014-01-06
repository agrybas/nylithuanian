#encoding=utf-8
from django.db import models, IntegrityError
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.template import Context
from django.template.loader import get_template
from django.core.signing import Signer
from django.core.mail import mail_admins
from articles.models import Article
import datetime
import random


class CreateUserError(Exception): pass


class UserProfileManager(models.Manager):
    def get_recent_users(self, limit=20):
        return self.model.objects.order_by('-user__date_joined', 'user__username')[:limit]

    def get_pending_users(self):
        return self.model.objects.order_by('user__username')


GENDER_LIST = (
    ('male', 'Vyras'),
    ('female', 'Moteris'),
)

RELATIONSHIP_TYPES = (
    ('single', 'Nevedęs/netekėjusi'),
    ('relationship', 'Turi draugą/draugę'),
    ('divorced', 'Išsiskyręs/išsiskyrusi'),
    ('widowed', 'Našlys/našlė'),
    ('married', 'Vedęs/ištekėjusi'),
    ('separated', 'Gyvena atskirai'),
)
SHIRT_SIZES = (
    ('XS', 'XS'),
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'),
    ('XL', 'XL'),
    ('XXL', 'XXL'),
)
USER_TYPES = (
    ('regular', 'Regular User'),
    ('admin', 'Administrator'),
    ('staff', 'Staff Member'),
    ('photographer', 'Photographer'),
    ('journalist', 'Journalist'),
)

# Reference model of independent countries, keyed by ISO-3166-1 alpha-3 code
class Country(models.Model):
    country_id = models.CharField(max_length = 3, primary_key = True)
    name = models.CharField(max_length = 45)
    formal_name = models.CharField(max_length = 80)
    
    class Meta:
        db_table = 'countries'
    
    def __unicode__(self):
        return self.name

# Data model containing all basic information about registered users
class UserProfile(models.Model):
    class Meta:
        db_table = 'site_users'
        # ordering = ['user.username']

    #userprofile_id = models.PositiveIntegerField(primary_key = True)
    user = models.OneToOneField(User, primary_key=True) # reference to the built-in User model
    password_old = models.CharField(max_length=32, blank=True)
    saved_new_password = models.BooleanField(
        default=False) # whether the user has set a new password (if not, site asks to do so on the next login)
    organization_title = models.CharField(max_length=100, blank=True) # if the user is an organization, its title
    gender = models.CharField(max_length=6, blank=True, choices=GENDER_LIST)
    birth_date = models.DateField(null=True, blank=True)
    relationship_status = models.CharField(max_length=12, blank=True, choices=RELATIONSHIP_TYPES)
    home_town = models.CharField(max_length=20, blank=True)
    home_country = models.ForeignKey(Country, null=True, blank=True)
    shirt_size = models.CharField(max_length=3, blank=True, choices=SHIRT_SIZES)
    temp_hash = models.CharField(max_length=32, blank=True, verbose_name='Temporary confirmation hash')
    user_type = models.CharField(max_length=15, blank=False, choices=USER_TYPES)
    favorite_articles = models.ManyToManyField(Article, related_name='article+', null=False, blank=True,
                                               verbose_name='Vartotojo mėgstami straipsniai') # articles marked as favorite

    objects = UserProfileManager()

    def __unicode__(self):
        return self.user.username

    def joined_recently(self):
        return self.user.date_joined >= timezone.now() - datetime.timedelta(days=7)

    # Generate hash for confirmation
    def generateHash(self):
        signer = Signer(salt=self.user.date_joined.strftime("%Y-%m-%d %H:%i:%s") + str(random.randint(1, 100)))
        self.temp_hash = signer.signature(self.user.username)
        self.save()
        return self.temp_hash

    def getHash(self):
        return self.temp_hash

    def getType(self):
        return self.user_type

    def setType(self, newType):
        TYPES_TO_GROUPS = {
            'regular': ['Regular', ],
            'admin': ['Administrators', 'Staff', 'Photographers', 'Journalists', 'Regular'],
            'staff': ['Staff', 'Photographers', 'Journalists', 'Regular'],
            'photographer': ['Photographers', 'Regular'],
            'journalist': ['Journalists', 'Regular'],
        }

        self.user_type = newType

        if newType == 'admin' or newType == 'staff':
            self.user.is_staff = True
        else:
            self.user.is_staff = False

        for groupName in TYPES_TO_GROUPS[newType]:
            group, _ = Group.objects.get_or_create(name=groupName)
            group.user_set.add(self.user)

        self.temp_hash = ''
        self.save()

        return True

    # Create a new user profile
    @staticmethod
    def createUser(username, email, password):
        try:
            user = User.objects.get(username=username)
            signer = Signer(salt=user.date_joined.strftime("%Y-%m-%d %H:%i:%s") + str(random.randint(1, 100)))
            regHash = signer.signature(user.username)    # registration confirmation hash
            UserProfile.objects.create(user=user, temp_hash=regHash, saved_new_password=True)

            return regHash
        except IntegrityError as e:
            # Duplicate entry
            if e.args[0] == 1062:
                raise CreateUserError(u'Toks vartotojo vardas jau užregistruotas.')
        except Exception as e:
            plainText = get_template('registration_error_email.txt')
            subject = u'Klaida vartotojo registracijos metu'
            c = Context({
                'username': username,
                'email_address': email,
                'error_message': e,
            })

            mail_admins(subject, plainText.render(c))
            raise CreateUserError(
                u'Klaidos priežastis nežinoma. Svetainės administratoriai buvo informuoti apie šią klaidą.')

            #class Organizer(models.Model):
            #    #organizer_id = models.PositiveIntegerField(primary_key = True)
            #    organization_title = models.CharField(max_length = 40, blank = True)
            #    first_name = models.CharField(max_length = 30, blank = True)
            #    last_name = models.CharField(max_length = 30, blank = True)
            #
            #    class Meta:
            #        db_table = 'organizers'
            #
            #    def __unicode__(self):
            #        if self.first_name:
            #            return u'%s %s' % (self.first_name, self.last_name)
            #        else:
            #            return self.organization_title

            # Data model containing addresses; allows to specify a title for concise references; allows to specify an address type; a Person entity can have multiple addresses;
            #class GenericAddress(models.Model):
            #    #address_id = models.PositiveIntegerField(primary_key = True)
            #    title = models.CharField(max_length = 20, blank = True) # title of the address (e.g. "Susivienijimas Lietuvių Amerikoje"), used to concisely reference an Address entity
            #    street_address1 = models.CharField(max_length = 30)
            #    street_address2 = models.CharField(max_length = 30, blank = True)
            #    street_address3 = models.CharField(max_length = 30, blank = True)
            #    street_address4 = models.CharField(max_length = 30, blank = True)
            #    city = models.CharField(max_length = 20, blank = True)
            #    zip_code = models.CharField(max_length = 10, blank = True)
            #    state = USStateField(blank = True, null = True)
            #    country = models.ForeignKey(Country, blank = True)
            #    type = models.CharField(max_length = 20, verbose_name='Address type') # e.g. Home address, Work address, Headquarters, etc.
            #    #entity = models.ForeignKey(Entity) # entity owning this address entry
            #
            #    class Meta:
            #        abstract = True
            #
            #    def __unicode__(self):
            #        if self.title:
            #            return self.title
            #        else:
            #            return self.street_address1
            #
            #class UserAddress(GenericAddress):
            #    user = models.ForeignKey(UserProfile) # site user owning this address entry
            #
            #    class Meta:
            #        db_table = 'user_addresses'

            #class AuthorAddress(GenericAddress):
            #    author = models.ForeignKey(Author) # author owning this address entry
            #
            #    class Meta:
            #        db_table = 'author_addresses'

            #class OrganizerAddress(GenericAddress):
            #    organizer = models.ForeignKey(Organizer) # organizer owning this address entry
            #
            #    class Meta:
            #        db_table = 'organizer_addresses'

            # Data model containing phones; allows to specify a phone type; a Person entity can have multiple phone numbers
            #class GenericPhone(models.Model):
            #    #phone_id = models.PositiveIntegerField(primary_key = True)
            #    country = models.ForeignKey(Country)
            #    number = models.CharField(max_length = 20)
            #    type = models.CharField(max_length = 20, verbose_name='Phone type') # e.g. Home phone, Cell phone, etc.
            #    #Entityt = models.ForeignKey(Entity) # entity owning this phone entry
            #
            #    class Meta:
            #        abstract = True
            #
            #    def __unicode__(self):
            #        return '%s (%s)' % (self.number, self.country.name)

            #class UserPhone(GenericPhone):
            #    user = models.ForeignKey(UserProfile) # site user owning this phone entry
            #
            #    class Meta:
            #        db_table = 'user_phones'

            #class AuthorPhone(GenericPhone):
            #    author = models.ForeignKey(Author) # author owning this phone entry
            #
            #    class Meta:
            #        db_table = 'author_phones'

            #class OrganizerPhone(GenericPhone):
            #    organizer = models.ForeignKey(Organizer) # organizer owning this phone entry
            #
            #    class Meta:
            #        db_table = 'organizer_phones'

            # Data model containing e-mails; allows to specify an e-mail type; a Person entity can have multiple e-mails
            # For a UserProfile entity, these are secondary e-mail addresses; the main e-mail address of a UserProfile entity
            # is specified in UserProfile.user.email field
            #class GenericEmail(models.Model):
            #    #email_id = models.PositiveIntegerField(primary_key = True)
            #    address = models.EmailField()
            #    type = models.CharField(max_length = 20, verbose_name='E-mail type') # e.g. Home e-mail, Work e-mail, etc.
            #    #entity = models.ForeignKey(Entity) # site user owning this e-mail entry
            #
            #    class Meta:
            #        abstract = True
            #
            #    def __unicode__(self):
            #        return self.address

            #class UserEmail(GenericEmail):
            #    user = models.ForeignKey(UserProfile) # site user owning this e-mail entry
            #
            #    class Meta:
            #        db_table = 'user_emails'

            #class AuthorEmail(GenericEmail):
            #    author = models.ForeignKey(Author) # author owning this e-mail entry
            #
            #    class Meta:
            #        db_table = 'author_emails'

            #class OrganizerEmail(GenericEmail):
            #    organizer = models.ForeignKey(Organizer) # organizer owning this e-mail entry
            #
            #    class Meta:
            #        db_table = 'organizer_emails'