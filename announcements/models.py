#encoding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings

class PublicAnnouncementsManager(models.Manager):
    def get_query_set(self):
        return super(PublicAnnouncementsManager, self).get_query_set().filter(is_approved=True)
    
class Announcement(models.Model):
    user = models.ForeignKey(User, related_name='user+', null=False, blank=False, editable=False) # user who created the post; only that user can edit or delete it
    title = models.CharField(null=False, blank=False, max_length=255, verbose_name='Pavadinimas')
    body = models.TextField(null=False, blank=False, verbose_name='Pranešimo tekstas', help_text='Tekstas turi būti rašomas naudojant <a target="_blank" href="http://en.wikipedia.org/wiki/Textile_%28markup_language%29">Textile</a> žymėjimo kalbą.')
    first_name = models.CharField(null=False, blank=True, max_length=30, verbose_name="Autoriaus vardas")
    last_name = models.CharField(null=False, blank=True, max_length=30, verbose_name="Autoriaus pavardė")
    organization_title = models.CharField(null=False, blank = True, max_length = 100, verbose_name="Organizacijos pavadinimas", help_text="Organizacija, kuriai priklauso autorius") # if the user is an organization, its title
    signature = models.CharField(null=False, blank=True, max_length=255, verbose_name="Autoriaus parašas", help_text="Papildoma informacija apie autorių") 
    phone_number = models.CharField(null=False, blank=True, max_length = 20, verbose_name="Telefono numeris", help_text="Autoriaus telefono numeris", validators=[RegexValidator(r'^[-0-9+() ]*$')])
    email_address = models.EmailField(null=False, blank=True, verbose_name="El. pašto adresas", help_text="Autoriaus elektroninio pašto adresas")
    create_date = models.DateTimeField(null=False, auto_now_add=True, verbose_name='Pranešimo ikelimo data', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"')
    modify_date = models.DateTimeField(null=False, auto_now=True, verbose_name='Pranešimo paskutinio redagavimo data', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"')
    is_approved = models.BooleanField(null=False, blank=False, default = False) # only approved announcements will ever be shown publicly; only administrator can change this value
    
    objects = models.Manager()
    public = PublicAnnouncementsManager()
    
    class Meta:
        db_table = 'announcements'
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return settings.SITE_URL + '/pranesimai/{0}'.format(self.id)
