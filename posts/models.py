#encoding=utf-8
from django.db import models
from users.models import Organizer
from django.contrib.auth.models import User
from static.models import Country
from django.contrib.localflavor.us.models import USStateField, USPostalCodeField
from django.contrib.localflavor.us.us_states import US_STATES
from django.utils import timezone

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

# Data model containing posts on the website which allow dynamic information updates
# (photo uploads, comments, favorites, etc.): articles, blogs, comments, etc.
# Only User entities can enter any posts, some posts require additional privileges
class GenericPost(models.Model):
    user = models.ForeignKey(User) # user who created the post; only that user can edit or delete it
    body = models.TextField()
    create_date = models.DateTimeField('Date when the post was created', editable= False, default = timezone.now())
    modify_date = models.DateTimeField('Date when the post was last modified', editable = False, default = timezone.now())
    publish_date = models.DateTimeField('Date when the post should be published', blank = True, null = True) # when a post should be published (shown publicly); null means publish immediately
    expiry_date = models.DateTimeField('Date when the post expires, i.e. is no longer visible publicly', blank = True, null = True)
    
    class Meta:
        abstract = True

class BlogPost(GenericPost):
    #post_id = models.PositiveIntegerField(primary_key = True, editable = False)
    title = models.CharField(max_length=45, blank = True)
    # reply_to = models.ForeignKey('self', blank = True)
    
    class Meta:
        db_table = 'blog_posts'
    
    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.body[:40]

# Data model for classifieds; classified does not require approval to be shown publicly; a classified can be associated with a photo album
# from the list of user's photo albums
class Classified(GenericPost):
    #classified_id = models.PositiveIntegerField(primary_key = True, editable = False)
    title = models.CharField(max_length=45)
    #photo_album = models.ForeignKey('PhotoAlbum')

    class Meta:
        db_table = 'classifieds'
        
    def __unicode__(self):
        return self.title
    
