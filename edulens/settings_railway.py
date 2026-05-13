"""
Railway.app uchun to'liq sozlamalar.
Bu fayl settings.py dan kengaytma qiladi va
barcha kerakli production sozlamalarini to'g'irlaydi.
"""
from .settings import *
import os
import dj_database_url

# ─── Asosiy ─────────────────────────────────────────
DEBUG      = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
# Railway avtomatik RAILWAY_PUBLIC_DOMAIN env o'rnatadi
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
_extra_hosts    = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
ALLOWED_HOSTS   = list(filter(None, [_railway_domain] + _extra_hosts)) or ['*']

# ─── PostgreSQL (majburiy) ───────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=DATABASE_URL.startswith('postgres'),
        )
    }
else:
    import sys
    print("⚠️  WARNING: DATABASE_URL topilmadi. SQLite ishlatilmoqda!", file=sys.stderr)
    # SQLite fallback (faqat test uchun, production da ma'lumotlar yo'qoladi!)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ─── Static fayllar (WhiteNoise) ────────────────────
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─── Email (production) ──────────────────────────────
EMAIL_HOST     = os.environ.get('EMAIL_HOST', '')
if EMAIL_HOST:
    EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS       = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'AvtoBaholash <noreply@avtobaho.uz>')
else:
    # Email sozlanmagan — logga yozamiz (parol tiklash ishlamaydi)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ─── Cache (Redis ixtiyoriy) ─────────────────────────
REDIS_URL = os.environ.get('REDIS_URL', '')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
# Redis yo'q bo'lsa LocMemCache ishlaydi (settings.py default)

# ─── Xavfsizlik ──────────────────────────────────────
SECURE_PROXY_SSL_HEADER    = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE      = True
CSRF_COOKIE_SECURE         = True
SECURE_BROWSER_XSS_FILTER  = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ─── Media fayllar ───────────────────────────────────
# Railway da fayl tizimi ephemeral — deploy bo'lsa fayllar yo'qoladi!
# S3 sozlangan bo'lsa ishlatiladi, aks holda lokal (faqat development)
AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET    = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION         = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

if AWS_ACCESS_KEY_ID and AWS_STORAGE_BUCKET:
    # S3 sozlangan — barcha media fayllar S3 da
    try:
        import storages  # django-storages
        AWS_S3_REGION_NAME              = AWS_S3_REGION
        AWS_DEFAULT_ACL                 = 'private'
        AWS_S3_FILE_OVERWRITE           = False
        AWS_QUERYSTRING_AUTH            = True
        AWS_QUERYSTRING_EXPIRE          = 3600  # 1 soat
        DEFAULT_FILE_STORAGE            = 'storages.backends.s3boto3.S3Boto3Storage'
        MEDIA_URL                       = f'https://{AWS_STORAGE_BUCKET}.s3.amazonaws.com/'
    except ImportError:
        # django-storages o'rnatilmagan
        import sys
        print("⚠️  django-storages o'rnatilmagan. pip install django-storages boto3", file=sys.stderr)
        MEDIA_ROOT = BASE_DIR / 'media'
        MEDIA_URL  = '/media/'
else:
    # S3 sozlanmagan — lokal (Railway da xavfli, faqat test uchun)
    MEDIA_ROOT = BASE_DIR / 'media'
    MEDIA_URL  = '/media/'
    if not DEBUG:
        import sys
        print("⚠️  OGOHLANTIRISH: S3 sozlanmagan! Media fayllar deploy da yo'qoladi.", file=sys.stderr)
        print("   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME o'rnating.", file=sys.stderr)

# ─── Logging ─────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '%(levelname)s %(asctime)s %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'},
    },
    'root': {'handlers': ['console'], 'level': 'WARNING'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'ERROR', 'propagate': False},
    },
}


# ─── Sentry (xato kuzatish — ixtiyoriy) ──────────────
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=False,
        )
    except ImportError:
        pass
