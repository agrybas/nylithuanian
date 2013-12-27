#encoding=utf-8
from django.db import models
from users.models import User
from django.utils import timezone


class Sympathy(models.Model):
    user = models.ForeignKey(User, editable=False) # user who created the post; only that user can edit or delete it
    #author = models.ForeignKey(ArticleAuthor, verbose_name="Straipsnio autorius")
    first_name = models.CharField(max_length=30, verbose_name="Autoriaus vardas")
    last_name = models.CharField(max_length=30, verbose_name="Autoriaus pavardė")
    organization_title = models.CharField(max_length = 100, verbose_name="Organizacijos pavadinimas", help_text="Organizacija, kuriai priklauso autorius", blank = True) # if the user is an organization, its title
    create_date = models.DateTimeField('Date when the post was created', editable= False)
    modify_date = models.DateTimeField('Date when the post was last modified', editable = False)
    title = models.CharField(max_length=100, verbose_name='Pavadinimas')
    body = models.TextField(verbose_name='Užuojautos tekstas', help_text='Tekstas turi būti rašomas naudojant <a target="_blank" href="http://en.wikipedia.org/wiki/Textile_%28markup_language%29">Textile</a> žymėjimo kalbą.')
    is_approved = models.BooleanField(default = False) # only approved articles will ever be shown publicly; only administrator can change this value
    
    class Meta:
        db_table = 'sympathies'
    
    def __unicode__(self):
        return self.title
    
class SympathyComment(models.Model):
    user = models.ForeignKey(User, editable=False) # user who created the post; only that user can edit or delete it
    sympathy = models.ForeignKey(Sympathy, editable = False)
    body = models.TextField(verbose_name='Komentaras')
    create_date = models.DateTimeField('Date when the post was created', editable= False, default = timezone.now())

    
    class Meta:
        db_table = 'sympathy_comments'
        
    def __unicode__(self):
        return self.user.username + ': ' + self.body[:50]
