
from pathlib import Path
import environ
import cloudinary


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(env_file=Path.joinpath(BASE_DIR, '.env'))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1nnn(1fvc%@@92)=cmx8n=x!ca%^d$*49l4#5v8a*l=(n3z9v2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'shop.apps.ShopConfig',
    'django.contrib.admin',
    'tailwind',
    # 'easy_thumbnails',
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
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# # thumbnail creators
# THUMBNAIL_ALIASES = {
#     '': {
#         'card_img': {'size': (200, 150), 'crop': True, 'quality': 80},
#         'card_detail_img': {'size': (400, 300), 'crop': True, 'quality': 80},
#     },
# }


WSGI_APPLICATION = 'biscuitshop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Tailwind CSS Configuration
TAILWIND_APP_NAME = 'theme'


SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
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
# Mvola API scopes - request the correct scope for merchant pay operations
MVOLA_API_SCOPE = env('MVOLA_API_SCOPE', default='merchantpay') #type: ignore