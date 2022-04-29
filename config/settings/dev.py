from .base import *
from .base import env


# Base
DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': "uni2data",
            'USER': "uni2data",
            'PASSWORD': "uni2data",
            # 'HOST': env('POSTGRES_HOST'),
            # 'PORT': env('POSTGRES_PORT'),
        }
}