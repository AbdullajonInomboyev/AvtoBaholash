from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Production da SECRET_KEY .env dan olinishi MAJBURIY
# Development uchun default qiymat (DEBUG=True bo'lganda)
import sys

_DEBUG_MODE = config('DEBUG', default=True, cast=bool)
SECRET_KEY  = config('SECRET_KEY', default='django-insecure-DEV-ONLY-CHANGE-IN-PRODUCTION')

if not _DEBUG_MODE and SECRET_KEY.startswith('django-insecure'):
    print("\n❌ XATO: Production da insecure SECRET_KEY ishlatilmoqda!", file=sys.stderr)
    print("   .env yoki environment variables ga SECRET_KEY o'rnating.", file=sys.stderr)
    print("   Generatsiya: python -c \"import secrets; print(secrets.token_urlsafe(50))\"\n", file=sys.stderr)
    sys.exit(1)
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',') + ['testserver']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # AvtoBaholash apps
    'accounts.apps.AccountsConfig',
    'core.apps.CoreConfig',
    'assessment.apps.AssessmentConfig',
    'analytics.apps.AnalyticsConfig',
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

ROOT_URLCONF = 'edulens.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'edulens.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')

# Telegram Bot Integration
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_DEFAULT_CHAT_ID = config('TELEGRAM_DEFAULT_CHAT_ID', default='')


# Email (production uchun SMTP ga almashtiring)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'AvtoBaholash <noreply@edulens.uz>'

GROQ_API_KEY = config('GROQ_API_KEY', default='')

# Default parol — ishga tushirishdan so'ng o'zgartiring!
DEFAULT_STUDENT_PASSWORD = config('DEFAULT_STUDENT_PASSWORD', default='AvtoBaho2024!')
