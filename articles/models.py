#encoding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Data model containing details about author of an article; allows an author
# not to be a registered user, but a registered user may be associated with one or more
# author instances
#class ArticleAuthor(models.Model):
#    user = models.ForeignKey(User, editable=False) # user to whom this article author entry belongs
#    first_name = models.CharField(max_length = 30)
#    last_name = models.CharField(max_length = 30)
#    email = models.EmailField(verbose_name="El. pašto adresas")
#    signature = models.TextField(verbose_name="Parašas", help_text="Papildomas tekstas, rodomas straipsnio pradžioje kartu su pagrindine informacija apie autorių.")
#    
#    class Meta:
#        db_table = 'article_authors'
#        
#    def __unicode__(self):
#        return u'%s %s' % (self.first_name, self.last_name)

class ArticleSource(models.Model):
    title = models.CharField(verbose_name='RSS straipsnio saltinis', max_length=20, editable = False)
    image = models.FilePathField(verbose_name='Straipsnio saltinio logo')
    
    class Meta:
        db_table = 'article_sources'
        
    def __unicode__(self):
        return self.title
    
class PublicArticlesManager(models.Manager):
    def get_query_set(self):
        return super(PublicArticlesManager, self).get_query_set().filter(is_approved=True).filter(publish_date__lte=timezone.now())

# Data model for articles; articles may contain a short summary that will be used to briefly introduce the article
# Article must be approved by administrator before it's shown publicly; Name and contact info shown next to article will be that of
# an author, not of the user who created the article entry; a user can select an author from a list of those associated with the user's account
class Article(models.Model):
    user = models.ForeignKey(User, related_name='user+', null=False, blank=False, editable=False) # user who created the post; only that user can edit or delete it
    #author = models.ForeignKey(ArticleAuthor, verbose_name="Straipsnio autorius")
    title = models.CharField(null=False, blank=False, max_length=255, verbose_name='Pavadinimas')
    body = models.TextField(null=False, blank=False, verbose_name='Straipsnio tekstas', help_text='Tekstas turi būti rašomas naudojant <a target="_blank" href="http://en.wikipedia.org/wiki/Textile_%28markup_language%29">Textile</a> žymėjimo kalbą.')
    first_name = models.CharField(null=False, blank=True, max_length=30, verbose_name="Autoriaus vardas")
    last_name = models.CharField(null=False, blank=True, max_length=30, verbose_name="Autoriaus pavardė")
    organization_title = models.CharField(null=False, blank = True, max_length = 100, verbose_name="Organizacijos pavadinimas", help_text="Organizacija, kuriai priklauso autorius") # if the user is an organization, its title
    signature = models.CharField(null=False, blank=True, max_length=255, verbose_name="Autoriaus parašas", help_text="Papildoma informacija apie autorių") 
    phone_number = models.CharField(null=False, blank=True, max_length = 20, verbose_name="Telefono numeris", help_text="Autoriaus telefono numeris")
    email_address = models.EmailField(null=False, blank=True, verbose_name="El. pašto adresas", help_text="Autoriaus elektroninio pašto adresas")
    create_date = models.DateTimeField(null=False, blank=False, default=timezone.now, verbose_name='Straipsnio ikelimo data', editable= False)
    modify_date = models.DateTimeField(null=False, blank=False, default=timezone.now, verbose_name='Straipsnio paskutinio redagavimo data', editable = False)
    publish_date = models.DateTimeField(null=False, blank=True, default=timezone.now, verbose_name='Publikavimo data')
    is_approved = models.BooleanField(null=False, blank=False, default = False) # only approved articles will ever be shown publicly; only administrator can change this value
    external_link = models.URLField(null=True, blank=True, verbose_name='Nuoroda į RSS straipsnį')
    source = models.ForeignKey(ArticleSource, null=True, blank=True, verbose_name='RSS straipsnio šaltinis')
    
    objects = models.Manager()
    public = PublicArticlesManager()
    
    class Meta:
        db_table = 'articles'
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return '/straipsniai/{0}'.format(self.id)
    
class ArticleComment(models.Model):
    user = models.ForeignKey(User, null=False, blank=False, editable=False) # user who created the post; only that user can edit or delete it
    article = models.ForeignKey(Article, null=False, blank=False, editable = False)
    body = models.TextField(null=False, blank=False, verbose_name='Komentaras')
    create_date = models.DateTimeField(null=False, blank=False, editable= False, default = timezone.now, verbose_name='Date when the post was created')

    
    class Meta:
        db_table = 'article_comments'
        
    def __unicode__(self):
        return self.user.username + ': ' + self.body[:50]

