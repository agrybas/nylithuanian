#encoding=utf-8
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class ClassifiedCategory(models.Model):
    title = models.CharField(null=False, blank=False, max_length=255, verbose_name='Kategorijos pavadinimas')

    class Meta:
        db_table = 'classified_categories'
        ordering = ['title']
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def __unicode__(self):
        return self.title
    
class ClassifiedSubCategory(models.Model):
    title = models.CharField(null=False, blank=False, max_length=255, verbose_name='Kategorijos pavadinimas')
    category = models.ForeignKey(ClassifiedCategory, null=False, blank=False)
    
    class Meta:
        db_table = 'classified_subcategories'
        ordering = ['category__title', 'title']
        verbose_name = 'sub-category'
        verbose_name_plural = 'sub-categories'
    
    def __unicode__(self):
        return self.category.title + ": " + self.title

class PublicClassifiedsManager(models.Manager):
    def get_query_set(self):
        return super(PublicClassifiedsManager, self).get_query_set().filter(is_approved=True)

class Classified(models.Model):
    user = models.ForeignKey(User, null=False, blank=False, editable=False) # user who created the post; only that user can edit or delete it
    category = models.ForeignKey(ClassifiedSubCategory, verbose_name="Skelbimo kategorija", null=False, blank=False)
    title = models.CharField(null=False, blank=False, max_length=255, verbose_name='Skelbimo pavadinimas')
    body = models.TextField(null=False, blank=False, verbose_name='Skelbimo tekstas', help_text='Tekstas turi būti rašomas naudojant <a target="_blank" href="http://en.wikipedia.org/wiki/Textile_%28markup_language%29">Textile</a> žymėjimo kalbą.')
    phone_number = models.CharField(null=False, blank=True, max_length=20, verbose_name="Telefono numeris")
    email_address = models.EmailField(null=False, blank=True, verbose_name="El. pašto adresas")
    create_date = models.DateTimeField(null=False, blank=False, default=timezone.now, editable=False, verbose_name='Skelbimo įkėlimo data', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"')
    modify_date = models.DateTimeField(null=False, blank=False, default=timezone.now, editable=False, verbose_name='Skelbimo paskutinio redagavimo data', help_text='Prašome datą įvesti formatu "yyyy-mm-dd hh:mm"')
    is_approved = models.BooleanField(null=False, blank=False, default=True) # only approved classifieds will ever be shown publicly; only administrator can change this value

    objects = models.Manager()
    public = PublicClassifiedsManager()

    class Meta:
        db_table = 'classifieds'
        ordering = ['-create_date']
    
    def __unicode__(self):
        return self.user.username + ': ' + self.title
    
    def get_absolute_url(self):
        return '/skelbimai/{0}'.format(self.id)
    
