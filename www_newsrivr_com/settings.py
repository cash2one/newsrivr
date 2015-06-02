# Django settings for www_newsrivr_com project.
# mongod --dbpath /Users/rabshakeh/data --rest
"""
<VirtualHost *:80>
  ServerName esther.active8.nl
  SetHandler python-program
  DocumentRoot /home/rabshakeh/www/esther_active8_nl
  PythonHandler django.core.handlers.modpython
  PythonPath "['/home/rabshakeh/www', '/home/rabshakeh/www/www_newsrivr_com'] + sys.path"
  SetEnv DJANGO_SETTINGS_MODULE www_newsrivr_com.settings
  SetEnv PYTHON_EGG_CACHE /tmp
  PythonDebug Off
  ErrorLog /usr/log/esther_active8_nl.log
</VirtualHost>
"""

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Newsrivr admin', 'erik@active8.nl'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

SESSION_COOKIE_DOMAIN=""
SESSION_COOKIE_SECURE=False


MONGOSERVER = 'localhost'
MONGOPORT = 27017

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = '/home/rabshakeh/www/www_newsrivr_com/static'
MEDIA_ROOT = '/home/rabshakeh/www_newsrivr_com/static'
MEDIA_ROOT = '/Users/rabshakeh/workspace/Newsrivr/www_newsrivr_com/static'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1gd44i=p@+=&qi44)rc98z5@q1z%dju!s#yakngw1r3!2$sztt'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
 
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'www_newsrivr_com.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/rabshakeh/www_newsrivr_com/templates",
    "/Users/rabshakeh/workspace/Newsrivr/www_newsrivr_com/templates"
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

EMAIL_HOST = "mail.xxx.nl"
EMAIL_HOST_PASSWORD = "xxx"
EMAIL_HOST_USER = "xxx"
