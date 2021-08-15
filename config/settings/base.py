"""
Django settings for sican_2018 project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import environ
import sys
import locale
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration



if sys.platform in ['win32']:
    locale.setlocale(locale.LC_ALL, "eso")

if sys.platform in ['linux2']:
    locale.setlocale(locale.LC_ALL, "es_CO.UTF-8")



ROOT_DIR = environ.Path(__file__) - 3 #cpe/config/settings/base.py - 3 = cpe
BASE_DIR = ROOT_DIR

env = environ.Env()
env.read_env(str(ROOT_DIR.path('.env')))


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', True)


# Celery settings

CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Bogota'



CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap', 'uni_form', 'bootstrap3', 'materialize_css_forms')
CRISPY_TEMPLATE_PACK = 'materialize_css_forms'




INTERNAL_IPS = ['localhost','127.0.0.1']


EMAIL_HOST = env('SICAN_EMAIL_HOST')
EMAIL_PORT = env('SICAN_EMAIL_PORT')
EMAIL_HOST_USER = env('SICAN_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('SICAN_EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('SICAN_DEFAULT_FROM_EMAIL')
EMAIL_DIRECCION_FINANCIERA = env('SICAN_EMAIL_DIRECCION_FINANCIERA')
EMAIL_GERENCIA = env('SICAN_EMAIL_GERENCIA')
EMAIL_CONTABILIDAD = env('SICAN_EMAIL_CONTABILIDAD')
EMAIL_REPRESENTANTE_LEGAL = env('SICAN_EMAIL_REPRESENTANTE_LEGAL')
EMAIL_RECURSO_HUMANO2 = env('EMAIL_RECURSO_HUMANO2')
EMAIL_USE_TLS = True

ADMINS = [('Diego Fonseca','dandresfsoto@gmail.com')]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env('CHANNEL_LAYERS_URL')],
        },
    },
}






REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SICAN_2018_SECRET_KEY')





ALLOWED_HOSTS = ['*']

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

INIT_URL = '/'

# Application definition

DJANGO_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'channels',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize'
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_forms_materialize',
    'django_celery_beat',
    'django_celery_results',
    'rest_framework',
    'phonenumber_field',
    'social_django',
    'django_cleanup',
    'mail_templated',
    'storages',
    'djmoney',
    'mathfilters'
]

LOCAL_APPS = [
    'usuarios',
    'recursos_humanos',
    'direccion_financiera',
    'reportes',
    'mis_contratos',
    'ofertas',
    'formacion',
    'entes_territoriales',
    'cpe_2018',
    'desplazamiento',
    'formatos',
    'fest_2019',
    'fest_2020_',
    'mobile'
]


INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.middleware.LoginRequiredMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware'
]

ROOT_URLCONF = 'config.urls'

USE_X_FORWARDED_HOST = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(BASE_DIR.path('templates')),
            str(BASE_DIR.path('media')),
        ]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect'
            ],
            'libraries':{
                'ofertas_tags': 'ofertas.templatetags.ofertas_tags',
            }
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

ASGI_APPLICATION = 'config.routing.application'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend'
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'es-CO'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = str(ROOT_DIR('staticfiles'))
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.

STATICFILES_DIRS = [
    str(BASE_DIR.path('static')),
]

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media
MEDIA_ROOT = str(BASE_DIR('media'))
MEDIA_URL = '/media/'




AUTH_USER_MODEL = "usuarios.User"
SOCIAL_AUTH_USER_MODEL = "usuarios.User"

LOGIN_EXEMPT_URLS = (
    r'^login/',
)



PHONENUMBER_DEFAULT_REGION = "CO"

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]



SOCIAL_AUTH_FACEBOOK_KEY = env('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = env('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_API_VERSION = '2.12'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'locale': 'es_CO',
  'fields': 'id, name, email, age_range'
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

SOCIAL_AUTH_TWITTER_KEY = env('SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = env('SOCIAL_AUTH_TWITTER_SECRET')

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    # 'social_core.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',

    # Save avatar.
    'config.pipeline.save_profile_picture',
)

FTP_STORAGE_LOCATION = env('FTP_SICAN_2018')

ATOMIC_REQUESTS = True

sentry_sdk.init(
    dsn=env('SENTRY_URL'),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration()
    ],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
