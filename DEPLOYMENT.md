# Production deployment on Liara

This project is prepared for Liara's Django PaaS.

## Production architecture

- Django application: Liara Django App
- Database: Liara PostgreSQL
- Uploaded media: Liara Disk mounted at `/app/media`
- Static files: WhiteNoise from the Django app
- HTTPS/domain: Liara

SQLite remains available only for local development. Production settings
refuse to start unless PostgreSQL configuration is present.

## 1. Create the PostgreSQL database

Create a PostgreSQL database in the Liara console.

Use the PostgreSQL connection values supplied by Liara as:

- `POSTGRESQL_DB_HOST`
- `POSTGRESQL_DB_PORT`
- `POSTGRESQL_DB_USER`
- `POSTGRESQL_DB_PASS`
- `POSTGRESQL_DB_NAME`

Do not commit these values to Git.

## 2. Create the Django application

Create a Django/Python application in Liara and connect it to this GitHub
repository and the `liara-production` branch.

The application must use:

```
DJANGO_SETTINGS_MODULE=clinic.settings_production
```

Set the production secret and domain variables in Liara's environment
settings.

## 3. Configure the media disk

Create a persistent Liara Disk and mount it at:

```
/app/media
```

The application already uses:

```
MEDIA_ROOT=/app/media
MEDIA_URL=/media/
```

Uploaded doctor/clinic/case images therefore survive application rebuilds.

## 4. Required environment variables

At minimum:

```
DJANGO_SETTINGS_MODULE=clinic.settings_production
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<random-production-secret>
DJANGO_ALLOWED_HOSTS=<your-domain>,<liara-app-domain>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-domain>
DJANGO_SECURE_SSL_REDIRECT=1
DJANGO_SESSION_COOKIE_SECURE=1
DJANGO_CSRF_COOKIE_SECURE=1
DJANGO_HSTS_SECONDS=31536000
MEDIA_ROOT=/app/media
```

Plus all five PostgreSQL variables from step 1.

## 5. First deployment

The production startup script runs:

1. `python manage.py migrate`
2. `python manage.py collectstatic --noinput`
3. Gunicorn

After the first successful deployment, create the admin account from the
Liara terminal:

```
python manage.py createsuperuser
```

Then run the clinic seed command if the production database is empty:

```
python manage.py seed_clinic
```

## 6. Domain and HTTPS

After the Liara application works on its generated domain, connect the
clinic's custom domain in Liara and update:

```
DJANGO_ALLOWED_HOSTS
DJANGO_CSRF_TRUSTED_ORIGINS
```

to the final domain(s). Keep HTTPS enabled.

## 7. Important production rule

Do not use `db.sqlite3` on Liara. PostgreSQL is the production database.
Do not store uploaded media only inside the application filesystem; use the
persistent Disk.
