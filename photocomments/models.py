from django.db import models
from django.contrib.auth.models import User
from photologue.models import Photo

class PhotoComment(models.Model):
    user = models.ForeignKey(User, editable=False) # user who uploaded the photo; only that user can edit or delete it
    photo = models.ForeignKey(Photo, editable = False)
    body = models.TextField(verbose_name='Komentaras')
    create_date = models.DateTimeField('Date when the comment was created', editable= False, default = timezone.now())

    class Meta:
        db_table = 'photo_comments'

    def __unicode__(self):
        return self.user.username + ': ' + self.body[:50]
