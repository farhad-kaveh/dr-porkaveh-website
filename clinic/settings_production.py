"""
Production settings.

Activate with:  DJANGO_SETTINGS_MODULE=clinic.settings_production

Everything security-sensitive comes from environment variables so no
secret is ever committed to the repository. See .env.example for the
full list of variables and DEPLOYMENT.md for how to set them.
"""
import os

from .settings import *  # noqa: F401,F403
from .settings import BASE_DIR, MIDDLEWARE

DEBUG = os.getenv('DJANGO_DEBUG', '0') == '1'

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError(
        'DJANGO_SECRET_KEY environment variable is not set. '
        'Generate one and set it before starting the production server.'
    )

ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]

# --- Static files (served directly by the app via WhiteNoise; no CDN required) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    *MIDDLEWARE[1:],  # keep every other middleware from the base list, in order
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = 'media/'

# --- HTTPS / transport security ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', '1') == '1'
SESSION_COOKIE_SECURE = os.getenv('DJANGO_SESSION_COOKIE_SECURE', '1') == '1'
CSRF_COOKIE_SECURE = os.getenv('DJANGO_CSRF_COOKIE_SECURE', '1') == '1'
SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# --- Optional PostgreSQL support (falls back to SQLite if DATABASE_URL is unset) ---
# Kept dependency-free: set DATABASE_URL like
#   postgres://USER:PASSWORD@HOST:PORT/DBNAME
_database_url = os.getenv('DATABASE_URL')
if _database_url:
    from urllib.parse import urlparse

    _parsed = urlparse(_database_url)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _parsed.path.lstrip('/'),
            'USER': _parsed.username,
            'PASSWORD': _parsed.password,
            'HOST': _parsed.hostname,
            'PORT': _parsed.port or 5432,
        }
    }
