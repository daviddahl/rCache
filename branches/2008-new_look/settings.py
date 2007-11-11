import os

# Django settings for rcache project.

DEBUG = True

SERVER_URL = os.environ['RCACHE_SERVER_URL']

EMAIL_HOST_USER = os.environ['RCACHE_EMAIL_USER']
EMAIL_HOST_PASSWORD = os.environ['RCACHE_EMAIL_HOST_PASSWORD']
EMAIL_PORT = os.environ['RCACHE_EMAIL_PORT']
EMAIL_TLS = True

TEMPLATE_DEBUG = DEBUG
#fixme: add admins to env vars
ADMINS = (
    ('David Dahl', 'david@ddahl.com'),
)
DEV_ENV = os.environ['RCACHE_SERVER_ENV']
MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'#'mysql_old'
DATABASE_NAME = os.environ['RCACHE_DB_NAME']
DATABASE_USER = os.environ.get('RCACHE_DB_USER','')
DATABASE_PASSWORD = os.environ.get('RCACHE_DB_PASSWD','')
DATABASE_HOST = os.environ.get('RCACHE_DB_HOST','')
DATABASE_PORT = os.environ.get('RCACHE_DB_PORT','')
# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.environ['RCACHE_DJANGO_MEDIA_ROOT']

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/site_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'kt$u+3q%ng(^=t^x-eto_r!uxn-n#a5=@wxrjcge!(ym1uy#7*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'rcache.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    os.environ['RCACHE_DJANGO_TMPL_DIR'],
#    '/home/david/code/rcache_django/rcache/tmpl',
#    '/Users/dahl/Code/rcache_django/tmpl',
#    '/home/rcachedev/code/dev/rcache/tmpl',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'rcache.account',
    'rcache',
)

ANTIWORD = '/usr/bin/antiword'
PDFTOTEXT = '/usr/bin/pdftotext'
