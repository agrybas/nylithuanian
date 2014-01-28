# encoding=utf-8
# TODO check all ForeignKey relationships for ON DELETE clause
import os
import random
from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_init
from django.utils.timezone import now
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.importlib import import_module
from django.utils.encoding import force_text
from django.utils.encoding import smart_str, filepath_to_uri
from django.utils.functional import curry
from django.utils import timezone

from .utils import EXIF
from .utils.watermark import apply_watermark

# Required PIL classes may or may not be available from the root namespace
# depending on the installation method used.
try:
    import Image
    import ImageFile
    import ImageFilter
    import ImageEnhance
except ImportError:
    try:
        from PIL import Image
        from PIL import ImageFile
        from PIL import ImageFilter
        from PIL import ImageEnhance
    except ImportError:
        raise ImportError(
            'Unable to import the Python Imaging Library. Please confirm it`s installed and available on your current Python path.')

# attempt to load the django-tagging TagField from default location,
# otherwise we substitute a dummy TagField.
try:
    from tagging.fields import TagField
    tagfield_help_text = 'Separate tags with spaces, put quotes around multiple-word tags.'
except ImportError:
    class TagField(models.CharField):

        def __init__(self, **kwargs):
            default_kwargs = {'max_length': 255, 'blank': True}
            default_kwargs.update(kwargs)
            super(TagField, self).__init__(**default_kwargs)

        def get_internal_type(self):
            return 'CharField'
    tagfield_help_text = 'Django-tagging was not found, tags will be treated as plain text.'

    # Tell South how to handle this custom field.
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^photos\.models\.TagField"])


# *** PREDEFINED CONSTANTS ***

# Default limit for gallery.latest
LATEST_LIMIT = getattr(settings, 'PHOTOS_GALLERY_LATEST_LIMIT', None)

# Number of random images from the gallery to display.
SAMPLE_SIZE = getattr(settings, 'PHOTOS_GALLERY_SAMPLE_SIZE', 5)

# Image path relative to media root
PHOTOS_DIR = getattr(settings, 'PHOTOS_DIR', 'photos')

# Path to sample image
SAMPLE_IMAGE_PATH = getattr(settings, 'PHOTOS_SAMPLE_IMAGE_PATH', os.path.join(
    os.path.dirname(__file__), 'static', 'sample.jpg'))  # os.path.join(settings.PROJECT_PATH, 'photos', 'static', 'sample.jpg')

# Look for user function to define file paths
PHOTOS_PATH = getattr(settings, 'PHOTOS_PATH', None)
if PHOTOS_PATH is not None:
    if callable(PHOTOS_PATH):
        get_storage_path = PHOTOS_PATH
    else:
        parts = PHOTOS_PATH.split('.')
        module_name = '.'.join(parts[:-1])
        module = import_module(module_name)
        get_storage_path = getattr(module, parts[-1])
else:
    def get_storage_path(instance, filename):
        return os.path.join(PHOTOS_DIR, 'photos', filename)

# choices for new crop_anchor field in Photo
CROP_ANCHOR_CHOICES = (
    ('top', 'Top'),
    ('right', 'Right'),
    ('bottom', 'Bottom'),
    ('left', 'Left'),
    ('center', 'Center (Default)'),
)

WATERMARK_STYLE_CHOICES = (
    ('tile', 'Tile'),
    ('scale', 'Scale'),
)

# Quality options for JPEG images
JPEG_QUALITY_CHOICES = (
    (30, 'Very Low'),
    (40, 'Low'),
    (50, 'Medium-Low'),
    (60, 'Medium'),
    (70, 'Medium-High'),
    (80, 'High'),
    (90, 'Very High'),
)


class Gallery(models.Model):
    title = models.CharField(verbose_name='Pavadinimas', max_length=100, unique=True)
    description = models.TextField(verbose_name='Aprašymas', blank=True)
    user = models.ForeignKey(User, blank=False, null=False, editable=False)  # user who created the gallery
    date_added = models.DateTimeField(verbose_name='Sukūrimo data', default=now)
    is_public = models.BooleanField(verbose_name='Publikuojamas viešai', default=True, help_text='Public galleries will be displayed in the default views.')
    tags = TagField(verbose_name='Raktiniai žodžiai', help_text='Raktinius žodžius atskirkite tarpeliais, raktines frazes įveskite kabutėse.')

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = 'gallery'
        verbose_name_plural = 'galleries'
        db_table = 'galleries'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/nuotraukos/gallery/{0}'.format(self.id)

    def latest(self, limit=LATEST_LIMIT, public=True):
        if not limit:
            limit = self.photo_count()
        if public:
            return self.public()[:limit]
        else:
            return self.photos.all()[:limit]

    def sample(self, count=None, public=True):
        """Return a sample of photos, ordered at random.
        If the 'count' is not specified, it will return a number of photos
        limited by the GALLERY_SAMPLE_SIZE setting.
        """
        if not count:
            count = SAMPLE_SIZE
        if count > self.photo_count():
            count = self.photo_count()
        if public:
            photo_set = self.public()
        else:
            photo_set = self.photo_set.all()
        return random.sample(set(photo_set), count)

    def photo_count(self, public=True):
        """Return a count of all the photos in this gallery."""
        if public:
            return self.public().count()
        else:
            return self.photo_set.all().count()
    photo_count.short_description = 'count'

    def public(self):
        """Return a queryset of all the public photos in this gallery."""
        return self.photo_set.filter(is_public=True)


class Photo(models.Model):
    image = models.ImageField(verbose_name='Nuotraukos failas', upload_to=get_storage_path, height_field='height', width_field='width')
    height = models.PositiveSmallIntegerField(verbose_name='Paveikslėlio aukštis', null=False, blank=False, editable=False, help_text='Paveikslėlio aukštis')
    width = models.PositiveSmallIntegerField(verbose_name='Paveikslėlio plotis', null=False, blank=False, editable=False, help_text='Paveikslėlio plotis')
    sort_number = models.PositiveIntegerField(verbose_name='Eilės numeris', editable=False, null=True, blank=True, help_text='Norėdami rūšiuoti nuotraukas albume specifine tvarka, šiame laukelyje nurodykite nuotraukos eilės numerį. Nenurodžius eilės numerio, nuotraukos bus rūšiuojamos pagal įkėlimo datą.')
    user = models.ForeignKey(User, blank=False, null=False, editable=False)  # user who created the gallery
    gallery = models.ForeignKey(Gallery, blank=False, null=False, verbose_name="Nuotraukų albumas", help_text='Jei nematote pasirinktinų albumų, pirmiausia turite juos <a href="/nuotraukos/albumai/pateikti">sukurti</a>.')  # TODO add limit_choices_to argument to restrict galleries to only those created by current user
    title = models.CharField(verbose_name='Nuotraukos pavadinimas', max_length=100, blank=True)
    description = models.TextField(verbose_name='Nuotraukos aprašymas', blank=True)
    date_taken = models.DateTimeField(verbose_name='Fotografijos data', null=True, blank=True, editable=False)
    date_added = models.DateTimeField(verbose_name='Nuotraukos įkėlimo data', null=False, blank=False, editable=False, default=now, help_text='Nuotraukos albume rūšiuojamos pagal šį laukelį (jei nenurodyta kitaip).')
    view_count = models.PositiveIntegerField(verbose_name='Peržiūrų skaičius', default=0, null=False, blank=False, editable=False)
    crop_from = models.CharField(verbose_name='Iškirpti nuo', blank=True, max_length=10, default='center', choices=CROP_ANCHOR_CHOICES)
    is_cover = models.BooleanField(verbose_name="Albumo viršelis", default=False)
    is_public = models.BooleanField(verbose_name='Publikuojama viešai', default=True, help_text='Viešai publikuojamos nuotraukos bus matomos visiems.')
    tags = TagField(verbose_name='Raktiniai žodžiai', help_text='Raktinius žodžius atskirkite tarpeliais, raktines frazes įveskite kabutėse.')

    class Meta:
        ordering = ['sort_number', '-date_added']
        get_latest_by = 'date_added'
        verbose_name = "photo"
        verbose_name_plural = "photos"
        db_table = 'photos'

    @property
    def EXIF(self):
        try:
            return EXIF.process_file(open(self.image.path, 'rb'))
        except:
            try:
                return EXIF.process_file(open(self.image.path, 'rb'), details=False)
            except:
                return {}

    def __unicode__(self):
        return self.title

    def admin_thumbnail(self):
        func = getattr(self, 'get_admin_thumbnail_url', None)
        if func is None:
            return 'An "admin_thumbnail" photo size has not been defined.'
        else:
            if hasattr(self, 'get_absolute_url'):
                return u'<a href="%s"><img src="%s"></a>' % \
                    (self.get_absolute_url(), func())
            else:
                return u'<a href="%s"><img src="%s"></a>' % \
                    (self.image.url, func())
    admin_thumbnail.short_description = 'Thumbnail'
    admin_thumbnail.allow_tags = True

    def cache_path(self):
        return os.path.join(os.path.dirname(self.image.path), "cache")

    def cache_url(self):
        return '/'.join([os.path.dirname(self.image.url), "cache"])

    def image_filename(self):
        return os.path.basename(force_text(self.image.path))

    def _get_filename_for_size(self, size):
        size = getattr(size, 'name', size)
        base, ext = os.path.splitext(self.image_filename())
        return ''.join([base, '_', size, ext])

    def _get_SIZE_photosize(self, size):
        return PhotoSizeCache().sizes.get(size)

    def _get_SIZE_size(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        if not self.size_exists(photosize):
            self.create_size(photosize)
        return Image.open(self._get_SIZE_filename(size)).size

    def _get_SIZE_url(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        if not self.size_exists(photosize):
            self.create_size(photosize)
        if photosize.increment_count:
            self.increment_count()
        return '/'.join([
            self.cache_url(),
            filepath_to_uri(self._get_filename_for_size(photosize.name))])

    def _get_SIZE_filename(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        return smart_str(os.path.join(self.cache_path(),
                                      self._get_filename_for_size(photosize.name)))

    def increment_count(self):
        self.view_count += 1
        models.Model.save(self)

    def add_accessor_methods(self, *args, **kwargs):
        for size in PhotoSizeCache().sizes.keys():
            setattr(self, 'get_%s_size' % size,
                    curry(self._get_SIZE_size, size=size))
            setattr(self, 'get_%s_photosize' % size,
                    curry(self._get_SIZE_photosize, size=size))
            setattr(self, 'get_%s_url' % size,
                    curry(self._get_SIZE_url, size=size))
            setattr(self, 'get_%s_filename' % size,
                    curry(self._get_SIZE_filename, size=size))

    def size_exists(self, photosize):
        func = getattr(self, "get_%s_filename" % photosize.name, None)
        if func is not None:
            if os.path.isfile(func()):
                return True
        return False

    def resize_image(self, im, photosize):
        cur_width, cur_height = im.size
        new_width, new_height = photosize.size
        if photosize.crop:
            ratio = max(float(new_width) / cur_width, float(new_height) / cur_height)
            x = (cur_width * ratio)
            y = (cur_height * ratio)
            xd = abs(new_width - x)
            yd = abs(new_height - y)
            x_diff = int(xd / 2)
            y_diff = int(yd / 2)
            if self.crop_from == 'top':
                box = (int(x_diff), 0, int(x_diff + new_width), new_height)
            elif self.crop_from == 'left':
                box = (0, int(y_diff), new_width, int(y_diff + new_height))
            elif self.crop_from == 'bottom':
                box = (int(x_diff), int(yd), int(x_diff + new_width), int(y))  # y - yd = new_height
            elif self.crop_from == 'right':
                box = (int(xd), int(y_diff), int(x), int(y_diff + new_height))  # x - xd = new_width
            else:
                box = (int(x_diff), int(y_diff), int(x_diff + new_width), int(y_diff + new_height))
            im = im.resize((int(x), int(y)), Image.ANTIALIAS).crop(box)
        else:
            if not new_width == 0 and not new_height == 0:
                ratio = min(float(new_width) / cur_width,
                            float(new_height) / cur_height)
            else:
                if new_width == 0:
                    ratio = float(new_height) / cur_height
                else:
                    ratio = float(new_width) / cur_width
            new_dimensions = (int(round(cur_width * ratio)),
                              int(round(cur_height * ratio)))
            if new_dimensions[0] > cur_width or \
               new_dimensions[1] > cur_height:
                if not photosize.upscale:
                    return im
            im = im.resize(new_dimensions, Image.ANTIALIAS)
        return im

    def create_size(self, photosize):
        if self.size_exists(photosize):
            return
        if not os.path.isdir(self.cache_path()):
            os.makedirs(self.cache_path())
        try:
            im = Image.open(self.image.path)
        except IOError:
            return
        # Save the original format
        im_format = im.format
        # Resize/crop image
        if im.size != photosize.size and photosize.size != (0, 0):
            im = self.resize_image(im, photosize)
        # Apply watermark if found
        if photosize.watermark is not None:
            im = photosize.watermark.post_process(im)
        # Save file
        im_filename = getattr(self, "get_%s_filename" % photosize.name)()
        try:
            if im_format != 'JPEG':
                try:
                    im.save(im_filename)
                    return
                except KeyError:
                    pass
            im.save(im_filename, 'JPEG', quality=int(photosize.quality), optimize=True)
        except IOError as e:
            if os.path.isfile(im_filename):
                os.unlink(im_filename)
            raise e

    def remove_size(self, photosize, remove_dirs=True):
        if not self.size_exists(photosize):
            return
        filename = getattr(self, "get_%s_filename" % photosize.name)()
        if os.path.isfile(filename):
            os.remove(filename)
        if remove_dirs:
            self.remove_cache_dirs()

    def clear_cache(self):
        cache = PhotoSizeCache()
        for photosize in cache.sizes.values():
            self.remove_size(photosize, False)
        self.remove_cache_dirs()

    def pre_cache(self):
        cache = PhotoSizeCache()
        for photosize in cache.sizes.values():
            if photosize.pre_cache:
                self.create_size(photosize)

    def remove_cache_dirs(self):
        try:
            os.removedirs(self.cache_path())
        except:
            pass

    def save(self, *args, **kwargs):
        if self.date_taken is None:
            try:
                exif_date = self.EXIF.get('EXIF DateTimeOriginal', None)
                if exif_date is not None:
                    d, t = str.split(exif_date.values)
                    year, month, day = d.split(':')
                    hour, minute, second = t.split(':')
                    self.date_taken = datetime(int(year), int(month), int(day),
                                               int(hour), int(minute), int(second))
            except:
                pass
        if self.date_taken is None:
            self.date_taken = now()
        if self._get_pk_val():
            self.clear_cache()
        super(Photo, self).save(*args, **kwargs)
        self.pre_cache()

    def delete(self, using=None):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (
            self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        # Files associated to a FileField have to be manually deleted:
        # https://docs.djangoproject.com/en/dev/releases/1.3/#deleting-a-model-doesn-t-delete-associated-files
        # http://haineault.com/blog/147/
        # The data loss scenarios mentioned in the docs hopefully do not apply
        path = self.image.path
        super(Photo, self).delete()
        os.remove(path)

    def get_absolute_url(self):
        return '/nuotraukos/photo/{0}'.format(self.id)

    def public_galleries(self):
        """Return the public galleries to which this photo belongs."""
        return self.galleries.filter(is_public=True)

    @property
    def previous_photo_exists(self):
        return Photo.objects.filter(gallery=self.gallery).filter(date_added__gt=self.date_added).exists()
    
    @property
    def next_photo_exists(self):
        return Photo.objects.filter(gallery=self.gallery).filter(date_added__lt=self.date_added).exists()
    
    @property
    def get_next_photo_url(self):
        try:
            photo = Photo.objects.filter(gallery=self.gallery).filter(date_added__lt=self.date_added)[0]
            return photo.get_absolute_url()
        except Photo.DoesNotExist:
            return None
    
    @property
    def get_previous_photo_url(self):
        try:
            photo = Photo.objects.filter(gallery=self.gallery).filter(id__gt=self.id).order_by('sort_number', 'date_added')[0]
            return photo.get_absolute_url()
        except Photo.DoesNotExist:
            return None
    

class Watermark(models.Model):
    image = models.ImageField(verbose_name='image', upload_to=PHOTOS_DIR + "/watermarks")
    style = models.CharField(verbose_name='style', max_length=5, choices=WATERMARK_STYLE_CHOICES, default='scale')
    opacity = models.FloatField(verbose_name='opacity', default=1, help_text="The opacity of the overlay.")
    name = models.CharField(verbose_name='name', max_length=30, unique=True)
    description = models.TextField(verbose_name='description', blank=True)

    class Meta:
        verbose_name = 'watermark'
        verbose_name_plural = 'watermarks'
        db_table = 'watermarks'

    def sample_dir(self):
        return os.path.join(settings.MEDIA_ROOT, PHOTOS_DIR, 'samples')

    def sample_url(self):
        return settings.MEDIA_URL + '/'.join([PHOTOS_DIR, 'samples', '%s %s.jpg' % (self.name.lower(), 'sample')])

    def sample_filename(self):
        return os.path.join(self.sample_dir(), '%s %s.jpg' % (self.name.lower(), 'sample'))

    def create_sample(self):
        if not os.path.isdir(self.sample_dir()):
            os.makedirs(self.sample_dir())
        try:
            im = Image.open(SAMPLE_IMAGE_PATH)
        except IOError:
            raise IOError('Unable to open the sample image: %s.' % SAMPLE_IMAGE_PATH)
        im = self.process(im)
        im.save(self.sample_filename(), 'JPEG', quality=90, optimize=True)

    def admin_sample(self):
        return u'<img src="%s">' % self.sample_url()
    admin_sample.short_description = 'Sample'
    admin_sample.allow_tags = True

    def pre_process(self, im):
        return im

    def post_process(self, im):
        mark = Image.open(self.image.path)
        return apply_watermark(im, mark, self.style, self.opacity)

    def process(self, im):
        im = self.pre_process(im)
        im = self.post_process(im)
        return im

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            os.remove(self.sample_filename())
        except:
            pass
        models.Model.save(self, *args, **kwargs)
        self.create_sample()
        for size in self.photo_sizes.all():
            size.clear_cache()
        # try to clear all related subclasses of Photo
        for prop in [prop for prop in dir(self) if prop[-8:] == '_related']:
            for obj in getattr(self, prop).all():
                obj.clear_cache()
                obj.pre_cache()

    def delete(self, using=None):
        try:
            os.remove(self.sample_filename())
        except:
            pass
        models.Model.delete(self)


class PhotoSize(models.Model):
    name = models.CharField(verbose_name='name', max_length=40, unique=True, help_text='Photo size name should contain only letters, numbers and underscores. Examples: "thumbnail", "display", "small", "main_page_widget".')
    width = models.PositiveIntegerField(verbose_name='width', default=0, help_text='If width is set to "0" the image will be scaled to the supplied height.')
    height = models.PositiveIntegerField(verbose_name='height', default=0, help_text='If height is set to "0" the image will be scaled to the supplied width')
    quality = models.PositiveIntegerField(verbose_name='quality', choices=JPEG_QUALITY_CHOICES, default=70, help_text='JPEG image quality.')
    upscale = models.BooleanField(verbose_name='upscale images?', default=False, help_text='If selected the image will be scaled up if necessary to fit the supplied dimensions. Cropped sizes will be upscaled regardless of this setting.')
    crop = models.BooleanField(verbose_name='crop to fit?', default=False, help_text='If selected the image will be scaled and cropped to fit the supplied dimensions.')
    pre_cache = models.BooleanField(verbose_name='pre-cache?', default=False, help_text='If selected this photo size will be pre-cached as photos are added.')
    increment_count = models.BooleanField(verbose_name='increment view count?', default=False, help_text='If selected the image\'s "view_count" will be incremented when this photo size is displayed.')
    watermark = models.ForeignKey('Watermark', null=True, blank=True, related_name='photo_sizes', verbose_name='watermark image')

    class Meta:
        ordering = ['width', 'height']
        verbose_name = 'photo size'
        verbose_name_plural = 'photo sizes'
        db_table = 'photosizes'

    def __unicode__(self):
        return self.name

    def clear_cache(self):
        for cls in Photo.__subclasses__():
            for obj in cls.objects.all():
                obj.remove_size(self)
                if self.pre_cache:
                    obj.create_size(self)
        PhotoSizeCache().reset()

    def clean(self):
        if self.crop is True:
            if self.width == 0 or self.height == 0:
                raise ValidationError("Can only crop photos if both width and height dimensions are set.")

    def save(self, *args, **kwargs):
        super(PhotoSize, self).save(*args, **kwargs)
        PhotoSizeCache().reset()
        self.clear_cache()

    def delete(self, using=None):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (
            self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        super(PhotoSize, self).delete()

    def _get_size(self):
        return (self.width, self.height)

    def _set_size(self, value):
        self.width, self.height = value
    size = property(_get_size, _set_size)


class PhotoSizeCache(object):
    __state = {"sizes": {}}

    def __init__(self):
        self.__dict__ = self.__state
        if not len(self.sizes):
            sizes = PhotoSize.objects.all()
            for size in sizes:
                self.sizes[size.name] = size

    def reset(self):
        self.sizes = {}

class PhotoComment(models.Model):
    user = models.ForeignKey(User, blank=False, null=False, editable=False) # user who uploaded the photo; only that user can edit or delete it
    photo = models.ForeignKey(Photo, blank=False, null=False, editable = False)
    body = models.TextField(verbose_name='Komentaras')
    create_date = models.DateTimeField(editable=False, blank=False, null=False, default=timezone.now())

    class Meta:
        db_table = 'photo_comments'

    def __unicode__(self):
        return self.user.username + ': ' + self.body[:50]


# Set up the accessor methods
def add_methods(sender, instance, signal, *args, **kwargs):
    """ Adds methods to access sized images (urls, paths)

    after the Photo model's __init__ function completes,
    this method calls "add_accessor_methods" on each instance.
    """
    if hasattr(instance, 'add_accessor_methods'):
        instance.add_accessor_methods()

# connect the add_accessor_methods function to the post_init signal
post_init.connect(add_methods)
