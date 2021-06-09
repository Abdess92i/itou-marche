"""
Django settings for itou_c4_api project.

Generated by 'django-admin startproject' using Django 3.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import routers
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '[KEY]'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    os.environ.get('CURRENT_HOST'),
]


# Application definition

AUTH_USER_MODEL = "users.User"
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'itou_c4_api',
    'c4_directory.apps.C4DirectoryConfig',
    'users.apps.UsersConfig',
    'cocorico.apps.CocoricoConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'itou_c4_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'itou_c4_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Compatible with clevercloud add-ons, but still portable (and fails if none found)
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': os.environ.get('POSTGRESQL_ADDON_HOST', os.environ['PG_HOST']),
        'PORT': os.environ.get('POSTGRESQL_ADDON_PORT', os.environ['PG_PORT']),
        'NAME': os.environ.get('POSTGRESQL_ADDON_DB', os.environ['PG_NAME']),
        'USER': os.environ.get('POSTGRESQL_ADDON_USER', os.environ['PG_USER']),
        'PASSWORD': os.environ.get('POSTGRESQL_ADDON_PASSWORD', os.environ['PG_PASSWORD']),
    },
    'structures' : {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_ADDON_DB', os.environ['MYSQL_DB']),
        'USER': os.environ.get('MYSQL_ADDON_USER', os.environ['MYSQL_USER']),
        'PASSWORD': os.environ.get('MYSQL_ADDON_PASSWORD', os.environ['MYSQL_PASSWORD']),
        'HOST': os.environ.get('MYSQL_ADDON_HOST', os.environ['MYSQL_HOST']),
        'PORT': os.environ.get('MYSQL_ADDON_PORT', os.environ['MYSQL_PORT']),
    }
}

# Needed as long as Cocorico database used as data source
DATABASE_ROUTERS = ['routers.CocoRouter']


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4
            }
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    # YOUR SETTINGS
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'API marché de l\'inclusion',
    'DESCRIPTION': 'Une initiative de la Plateforme de l\'inclusion',
    'VERSION': '0.1.0',
    # OTHER SETTINGS
}
