#puzzle.configs.production.settings

#django
#local
from woot.settings.common import *

#util
from os import environ

########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## DATABASE CONFIGURATION
DATABASE_USER = environ.get('DB_USER')
DATABASE_PWD = environ.get('DB_PWD')

#mysql: https://github.com/PyMySQL/mysqlclient-python
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2' for PG
    'NAME': '',
    'USER': '',
    'PASSWORD': '',
    'HOST': '', # Set to empty string for localhost.
    'PORT': '', # Set to empty string for default.
  }
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
CACHES = {
  'default': {
    'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    'LOCATION': '127.0.0.1:11211',
  }
}
########## END CACHE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = 'd3&3@fq+6_6fpa3dh%r0dwhxz*n!+@p9&6l!6%sqw($&j4^_ym'
########## END SECRET CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'your_email@example.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER
########## END EMAIL CONFIGURATION
