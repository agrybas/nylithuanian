# NYLITHUANIAN SETTINGS - PRODUCTION
import settings-prod.private.py

CELERYD_NODES = "w1"
CELERYD_MULTI = "$CELERYD_CHDIR/manage.py celeryd_multi"
CELERYCTL = "$CELERYD_CHDIR/manage.py celeryctl"
CELERY_ENABLE_UTC = False
#CELERY_TIMEZONE = "US/Eastern"
CELERYD_OPTS = "--time-limit=300 --concurrency=8"
CELERYD_LOG_FILE = "/var/log/celery/celery.log"
CELERYD_PID_FILE = "/var/run/celery/celery.pid"

# from datetime import timedelta
# import  djcelery
# djcelery.setup_loader()
# 
# CELERYBEAT_SCHEDULE = {
#                        'atnaujinti-delfi-straipsnius' : {
#                                                          'task' : 'articles.tasks.pull_rss_articles',
#                                                          'schedule' : timedelta(minutes=1),
#                                                          'args' : ('http://www.delfi.lt/rss/feeds/emigrants.xml',)
#                                                          },
# 
#                        'atnaujinti-balsas-straipsnius' : {
#                                                          'task' : 'articles.tasks.pull_rss_articles',
#                                                          'schedule' : timedelta(minutes=1),
#                                                          'args' : ('http://www.balsas.lt/rss/sarasas/85',)
#                                                          },
#                        
#                        'atnaujinti-lrytas-straipsnius' : {
#                                                          'task' : 'articles.tasks.pull_rss_articles',
#                                                          'schedule' : timedelta(minutes=1),
#                                                          'args' : ('http://www.lrytas.lt/rss/?tema=37',)
#                                                          },
#                        }

DEBUG = False
SITE_URL = 'https://www.nylithuanian.org'

MANAGERS = ADMINS
SEND_BROKEN_LINK_EMAILS = True

ALLOWED_HOSTS = [
                 'www.nylithuanian.org',
                 ]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'lt'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

LOGIN_REDIRECT_URL = '/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files

STATICFILES_DIRS = (
                    SITE_ROOT + 'nylithuanian/static/',
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

# FILE_UPLOAD_HANDLERS = (
#    'django.core.files.uploadhandler.MemoryFileUploadHandler',
#    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
# )

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # this is the default, but specifying explicitly
EMAIL_FILE_PATH = '/tmp/email' # if using filebased EmailBackend (for testing)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'nylithuanian.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'nylithuanian.wsgi.application'

TEMPLATE_DIRS = (
    SITE_ROOT + 'nylithuanian/templates',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_markwhat',
#     'django.contrib.markup',
    'users',
    'events',
    'articles',
    'photos',
    'classifieds',
    'announcements',
    'newsletters',
    'djcelery'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
                   'verbose': {
                               'format': '%(asctime)s %(process)d - %(module)s - %(levelname)s: %(message)s',
                               'datefmt': '%dd%mmm%YYYY %H:%M:%S'
                               },
                   'simple': {
                              'format': '%(asctime)s %(levelname)s: %(message)s',
                              'datefmt': '%d%b%Y %H:%M:%S'
                              },
                   },
     'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse'
         }
     },
    'handlers': {
                    'console': {
                              'level': 'DEBUG',
                              'class': 'logging.StreamHandler',
                              'formatter': 'simple'
                              },
                    'debug': {
                           'level': 'DEBUG',
                           'class': 'logging.handlers.TimedRotatingFileHandler',
                           'when': 'd',
                           'utc': True,
                           'backupCount': 100,
                           'filename': LOGGING_ROOT + 'debug/main.log',
                           'formatter': 'simple'
                           },
                    'debug.articles': {
                                     'level': 'DEBUG',
                                     'class': 'logging.handlers.TimedRotatingFileHandler',
                                     'when': 'd',
                                     'utc': True,
                                     'backupCount': 100,
                                     'formatter': 'simple',
                                     'filename': LOGGING_ROOT + 'debug/articles.log'
                                     },
                    'debug.events': {
                                     'level': 'DEBUG',
                                     'class': 'logging.handlers.TimedRotatingFileHandler',
                                     'when': 'd',
                                     'utc': True,
                                     'backupCount': 100,
                                     'formatter': 'simple',
                                     'filename': LOGGING_ROOT + 'debug/events.log'
                                     },
                    'debug.newsletters': {
                                     'level': 'DEBUG',
                                     'class': 'logging.handlers.TimedRotatingFileHandler',
                                     'when': 'd',
                                     'utc': True,
                                     'backupCount': 100,
                                     'formatter': 'simple',
                                     'filename': LOGGING_ROOT + 'debug/newsletters.log'
                                     },
                    'debug.photos': {
                                     'level': 'DEBUG',
                                     'class': 'logging.handlers.TimedRotatingFileHandler',
                                     'when': 'd',
                                     'utc': True,
                                     'backupCount': 100,
                                     'formatter': 'simple',
                                     'filename': LOGGING_ROOT + 'debug/photos.log'
                                     },
                    'production': {
                                 'level': 'INFO',
                                 'class': 'logging.handlers.TimedRotatingFileHandler',
                                 'when': 'd',
                                 'utc': True,
                                 'backupCount': 100,
                                 'filename': LOGGING_ROOT + 'prod/main.log',
                                 'formatter': 'simple'
                           },
                    'production.articles': {
                                     'level': 'DEBUG',
                                     'class': 'logging.handlers.TimedRotatingFileHandler',
                                     'when': 'd',
                                     'utc': True,
                                     'backupCount': 100,
                                     'formatter': 'simple',
                                     'filename': LOGGING_ROOT + 'prod/articles.log'
                                     },
                    'production.events': {
                                     'level': 'DEBUG',
                                     'class': 'logging.handlers.TimedRotatingFileHandler',
                                     'when': 'd',
                                     'utc': True,
                                     'backupCount': 100,
                                     'formatter': 'simple',
                                     'filename': LOGGING_ROOT + 'prod/events.log'
                                     },
                    'production.newsletters': {
                                     'level': 'DEBUG',
                                     'class': 'logging.handlers.TimedRotatingFileHandler',
                                     'when': 'd',
                                     'utc': True,
                                     'backupCount': 100,
                                     'formatter': 'simple',
                                     'filename': LOGGING_ROOT + 'prod/newsletters.log'
                                     },
                    'production.photos': {
                                     'level': 'DEBUG',
                                     'class': 'logging.handlers.TimedRotatingFileHandler',
                                     'when': 'd',
                                     'utc': True,
                                     'backupCount': 100,
                                     'formatter': 'simple',
                                     'filename': LOGGING_ROOT + 'prod/photos.log'
                                     },
                    'mail_admins': {
                                  'level': 'ERROR',
                                 'filters': ['require_debug_false'],
                                  'formatter': 'verbose',
                                  'class': 'django.utils.log.AdminEmailHandler'
                                  }
                 },
    'loggers': {
                'debug': {
                          'handlers': ['console', 'debug'],
                          'level': 'DEBUG',
                          'propagate': False,
                          },
                'debug.articles': {
                                   'handlers': ['debug.articles'],
                                   'propagate': False,
                                   },
                'debug.events': {
                                   'handlers': ['debug.events'],
                                   'propagate': False,
                                   },
                'debug.newsletters': {
                                   'handlers': ['debug.newsletters'],
                                   'propagate': False,
                                   },
                'debug.photos': {
                                   'handlers': ['debug.photos'],
                                   'propagate': False,
                                   },
                'production': {
                               'handlers': ['production', 'mail_admins'],
                               'level': 'INFO',
                               'propagate': False
                               },
                'production.articles': {
                                   'handlers': ['production.articles'],
                                   'propagate': False,
                                   },
                'production.events': {
                                   'handlers': ['production.events'],
                                   'propagate': False,
                                   },
                'production.newsletters': {
                                   'handlers': ['production.newsletters'],
                                   'propagate': False,
                                   },
                'production.photos': {
                                   'handlers': ['production.photos'],
                                   'propagate': False,
                                   }
                }
}
