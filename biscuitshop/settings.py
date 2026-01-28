# import sys
from pathlib import Path
import environ
import cloudinary
# import dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(env_file=Path.joinpath(BASE_DIR, '.env'))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False) #type: ignore

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost']) #type: ignore


# Application definition

INSTALLED_APPS = [
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'shop.apps.ShopConfig',
    'django.contrib.admin',
    'tailwind',
    'theme.apps.ThemeConfig',
    'cloudinary', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'shop.middleware.CartMiddleware',
    'shop.middleware.WishlistMiddleware',
]

ROOT_URLCONF = 'biscuitshop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.cart.context_processors.cart',
                'shop.wishlist.context_processors.wishlist',
            ],
        },
    },
]

# logging config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',  # path to your log file
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        
        'shop': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


#cloudinary config
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
    'STATICFILES_STORAGE': None,
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
)

# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
# DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


WSGI_APPLICATION = 'biscuitshop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


# DATABASES = {
#     'default': dj_database_url.config(
#         default=env('DATABASE_URL'),
#         conn_max_age=600,
#         ssl_require=True
#     )
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# if 'test' in sys.argv:
#     DATABASES['default'] = {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'shop/static']
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        # "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Tailwind CSS Configuration
TAILWIND_APP_NAME = 'theme'

INTERNAL_IPS = [
    "127.0.0.1",
]


SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600                            # 2 weeks in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

ENV_MODE = env('ENV_MODE')

# Mvola API constant
MVOLA_API_URL = env('SANDBOX_MVOLA_API_URL') if ENV_MODE == 'sandbox' else env('PRODUCTION_MVOLA_API_URL')
MVOLA_CLIENT_ID = env('SANDBOX_MVOLA_CLIENT_ID') if ENV_MODE == 'sandbox' else env('PRODUCTION_MVOLA_CLIENT_ID')
MVOLA_SECRET_KEY = env('SANDBOX_MVOLA_SECRET_KEY') if ENV_MODE == 'sandbox' else env('PRODUCTION_MVOLA_SECRET_KEY')
MVOLA_PARTNER_MSISDN = env('SANDBOX_MVOLA_PARTNER_MSISDN') if ENV_MODE == 'sandbox' else env('PRODUCTION_MVOLA_PARTNER_MSISDN')
MVOLA_PARTNER_NAME = env('MVOLA_PARTNER_NAME')
MVOLA_ACCESS_TOKEN_ENDPOINT = env('SANDBOX_MVOLA_ACCESS_TOKEN_ENDPOINT') if ENV_MODE == 'sandbox' else env('PRODUCTION_MVOLA_ACCESS_TOKEN_ENDPOINT')
MVOLA_REVOKE_ENDPOINT = env('SANDBOX_MVOLA_REVOKE_ENDPOINT') if ENV_MODE == 'sandbox' else env('PRODUCTION_MVOLA_REVOKE_ENDPOINT')
MVOLA_API_SCOPE = env('MVOLA_API_SCOPE', default='EXT_INT_MVOLA_SCOPE') #type: ignore



#django security
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)