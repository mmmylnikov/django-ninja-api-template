import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


config = {
    'DEBUG': os.environ.get('DEBUG'),
    'DEBUG_HOST': os.environ.get('DEBUG_HOST'),
    'DEBUG_PORT': os.environ.get('DEBUG_PORT'),
    'LANGUAGE_CODE': os.environ.get('LANGUAGE_CODE'),
    'TIME_ZONE': os.environ.get('TIME_ZONE'),
    'SECRET_KEY': os.environ.get('SECRET_KEY'),
    'ALLOWED_HOSTS': os.environ.get('ALLOWED_HOSTS'),
    'DB_ENGINE': os.environ.get('DB_ENGINE'),
    'DB_NAME': os.environ.get('DB_NAME'),
    'DB_USER': os.environ.get('DB_USER'),
    'DB_PASSWORD': os.environ.get('DB_PASSWORD'),
    'DB_PASSWORD_ROOT': os.environ.get('DB_PASSWORD_ROOT'),
    'DB_HOST': os.environ.get('DB_HOST'),
    'DB_PORT': os.environ.get('DB_PORT'),
    'CELERY_BROKER_URL': os.environ.get('CELERY_BROKER_URL'),
    'CELERY_RESULT_BACKEND': os.environ.get('CELERY_RESULT_BACKEND'),
    'GRPC_SERVER_HOST': os.environ.get('GRPC_SERVER_HOST'),
    'GRPC_SERVER_PORT': os.environ.get('GRPC_SERVER_PORT'),
}


SECRET_KEY = config.get('SECRET_KEY')

DEBUG = (config.get('DEBUG') or 'False').lower() == 'true'

ALLOWED_HOSTS = (config.get('ALLOWED_HOSTS') or 'localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'events.apps.EventsConfig',
    'notifications.apps.NotificationsConfig',
    'django_celery_results',
    'django_celery_beat',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': config.get('DB_ENGINE'),
        'NAME': config.get('DB_NAME'),
        'USER': config.get('DB_USER'),
        'PASSWORD': config.get('DB_PASSWORD'),
        'HOST': config.get('DB_HOST'),
        'PORT': config.get('DB_PORT'),
    }
}

PASSWORD_VALIDATORS = [
    'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    'django.contrib.auth.password_validation.MinimumLengthValidator',
    'django.contrib.auth.password_validation.CommonPasswordValidator',
    'django.contrib.auth.password_validation.NumericPasswordValidator',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': validator} for validator in PASSWORD_VALIDATORS
]


LANGUAGE_CODE = config.get('LANGUAGE_CODE') or 'en-us'

TIME_ZONE = config.get('TIME_ZONE') or 'UTC'

USE_TZ = True

USE_I18N = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

NINJA_PAGINATION_PER_PAGE = int(config.get('PAGINATION_PER_PAGE') or '10')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}


CELERY_BROKER_URL = config.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config.get('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_RESULT_EXTENDED = True

GRPC_SERVER_HOST = config.get('GRPC_SERVER_HOST') or 'localhost'
GRPC_SERVER_PORT = int(config.get('GRPC_SERVER_PORT') or '50051')
