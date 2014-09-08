# NYLITHUANIAN SETTINGS - QA
execfile('nylithuanian/settings_qa.private.py')

DEBUG = False

MANAGERS = ADMINS
SEND_BROKEN_LINK_EMAILS = True

ALLOWED_HOSTS = [
                 '.nylithuanian.org',
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

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"

MEDIA_ROOT = SITE_ROOT + 'assets/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

STATIC_ROOT = SITE_ROOT + 'static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

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
EMAIL_FILE_PATH = SITE_ROOT + 'nylithuanian/tmp/email'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
)

SECURE_HSTS_SECONDS = 31536000 # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_FRAME_DENY = True # prevent clickjacking
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

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
    'django.contrib.markup',
    'users',
    'events',
    'articles',
#    'greetings',
#    'sympathies',
    'photos',
    'classifieds',
    'announcements'
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
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
                          'filename': LOGGING_ROOT + 'logs/debug/main.log',
                          'formatter': 'simple'
                          },
                 'debug.articles': {
                                    'level': 'DEBUG',
                                    'class': 'logging.handlers.TimedRotatingFileHandler',
                                    'when': 'd',
                                    'utc': True,
                                    'backupCount': 100,
                                    'formatter': 'simple',
                                    'filename': LOGGING_ROOT + 'logs/debug/articles.log'
                                    },
                 'debug.events': {
                                    'level': 'DEBUG',
                                    'class': 'logging.handlers.TimedRotatingFileHandler',
                                    'when': 'd',
                                    'utc': True,
                                    'backupCount': 100,
                                    'formatter': 'simple',
                                    'filename': LOGGING_ROOT + 'logs/debug/events.log'
                                    },
                 'production': {
                                'level': 'INFO',
                                'class': 'logging.handlers.TimedRotatingFileHandler',
                                'when': 'd',
                                'utc': True,
                                'backupCount': 100,
                                'filename': LOGGING_ROOT + 'logs/prod/main.log',
                                'formatter': 'simple'
                          },
                 'production.articles': {
                                'level': 'INFO',
                                'class': 'logging.handlers.TimedRotatingFileHandler',
                                'when': 'd',
                                'utc': True,
                                'backupCount': 100,
                                'filename': LOGGING_ROOT + 'logs/prod/articles.log',
                                'formatter': 'simple'
                          },
                 'production.events': {
                                'level': 'INFO',
                                'class': 'logging.handlers.TimedRotatingFileHandler',
                                'when': 'd',
                                'utc': True,
                                'backupCount': 100,
                                'filename': LOGGING_ROOT + 'logs/prod/events.log',
                                'formatter': 'simple'
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
                'production': {
                               'handlers': ['production', 'mail_admins'],
                               'level': 'INFO',
                               'propagate': False
                               }
                }
}
