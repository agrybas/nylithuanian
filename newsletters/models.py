#encoding=utf-8
from django.db import models
from django.conf import settings

class PublicNewslettersManager(models.Manager):
    def get_query_set(self):
        return super(PublicNewslettersManager, self).get_query_set().filter(is_approved=True)
    
class Newsletter(models.Model):
    title = models.CharField(null=False, blank=False, max_length=255, verbose_name='Pavadinimas')
    body = models.TextField(null=False, blank=False, verbose_name='Naujienlaiškio tekstas', help_text='Tekstas turi būti rašomas naudojant <a target="_blank" href="http://en.wikipedia.org/wiki/Textile_%28markup_language%29">Textile</a> žymėjimo kalbą.')
    create_date = models.DateTimeField(null=False, auto_now_add=True, verbose_name='Naujienlaiškio sukūrimo data', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"')
    modify_date = models.DateTimeField(null=False, auto_now=True, verbose_name='Naujienlaiškio paskutinio redagavimo data', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"')
    send_date = models.DateTimeField(null=True, blank=True, editable=False, verbose_name='Naujienlaiškio išsiuntimo data', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"')
    is_approved = models.BooleanField(null=False, blank=False, default = False) # only approved announcements will ever be shown publicly; only administrator can change this value
    
    objects = models.Manager()
    public = PublicNewslettersManager()
    
    class Meta:
        db_table = 'newsletters'
        ordering = ['-create_date', ]
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return settings.SITE_URL + '/naujienlaiskiai/{0}'.format(self.id)