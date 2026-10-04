"""Production settings for Liara / other production hosts.

Activate with: DJANGO_SETTINGS_MODULE=clinic.settings_production

All security-sensitive values come from environment variables.
"""
import os
from pathlib import Path
from urllib.parse import urlparse

from .settings import *  # noqa: F401,F403
from .settings import BASE_DIR, MIDDLEWARE

DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "DJANGO_SECRET_KEY environment variable is not set. "
        "Generate one and set it before starting the production server."
    )

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if h.strip()
]
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

# Static files are served by WhiteNoise.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Liara Disk should be mounted at /app/media (or another path supplied
# through MEDIA_ROOT). This keeps uploaded files outside the ephemeral
# application container filesystem.
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", str(BASE_DIR / "media")))
MEDIA_URL = "/media/"

# HTTPS / transport security.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "1") == "1"
SESSION_COOKIE_SECURE = os.getenv("DJANGO_SESSION_COOKIE_SECURE", "1") == "1"
CSRF_COOKIE_SECURE = os.getenv("DJANGO_CSRF_COOKIE_SECURE", "1") == "1"
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Production must use PostgreSQL. Liara can expose the database either
# through a DATABASE_URL or through its POSTGRESQL_DB_* environment vars.
_database_url = os.getenv("DATABASE_URL")
if _database_url:
    _parsed = urlparse(_database_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _parsed.path.lstrip("/"),
            "USER": _parsed.username,
            "PASSWORD": _parsed.password,
            "HOST": _parsed.hostname,
            "PORT": _parsed.port or 5432,
        }
    }
else:
    _db_required = [
        "POSTGRESQL_DB_HOST",
        "POSTGRESQL_DB_PORT",
        "POSTGRESQL_DB_USER",
        "POSTGRESQL_DB_PASS",
        "POSTGRESQL_DB_NAME",
    ]
    _missing_db_vars = [name for name in _db_required if not os.getenv(name)]
    if _missing_db_vars:
        raise RuntimeError(
            "Production PostgreSQL configuration is missing: "
            + ", ".join(_missing_db_vars)
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRESQL_DB_NAME"],
            "USER": os.environ["POSTGRESQL_DB_USER"],
            "PASSWORD": os.environ["POSTGRESQL_DB_PASS"],
            "HOST": os.environ["POSTGRESQL_DB_HOST"],
            "PORT": os.environ["POSTGRESQL_DB_PORT"],
        }
    }
