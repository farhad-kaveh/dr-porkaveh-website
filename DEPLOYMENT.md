# Deployment Guide

This project ships with production settings (`clinic.settings_production`),
Gunicorn, WhiteNoise (for serving static files without a separate CDN), a
Dockerfile, and a docker-compose file. You can deploy it either with Docker
or directly on a VPS.

## 0. Before you start

You will need:
- A domain name pointed at your server (e.g. `drporkave.com`).
- A server or hosting provider that lets you run Docker or Python (any
  basic Linux VPS works — 1 CPU / 1GB RAM is enough for this site).
- A reverse proxy or load balancer that terminates HTTPS (e.g. Caddy,
  Nginx + Certbot, or your hosting provider's built-in HTTPS). This
  project does not generate its own TLS certificates.

## 1. Generate a secret key

Run this once and save the output somewhere safe (a password manager is
fine):

```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 2. Create your `.env` file

Copy the example and fill in real values:

```
cp .env.example .env
```

Edit `.env`:

```
DJANGO_SETTINGS_MODULE=clinic.settings_production
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<paste the key from step 1>
DJANGO_ALLOWED_HOSTS=drporkave.com,www.drporkave.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://drporkave.com,https://www.drporkave.com
DJANGO_SECURE_SSL_REDIRECT=1
DJANGO_SESSION_COOKIE_SECURE=1
DJANGO_CSRF_COOKIE_SECURE=1
DJANGO_HSTS_SECONDS=31536000
```

**Never commit `.env` to version control** — it's already listed in
`.gitignore`.

If your reverse proxy handles HTTPS termination for you and the app itself
only ever receives plain HTTP from the proxy on your internal network, make
sure the proxy sets the `X-Forwarded-Proto` header — the app is already
configured to trust that header (`SECURE_PROXY_SSL_HEADER`), but only
enable this once you're sure external traffic can't spoof it directly.

## 3. Deploy with Docker (recommended)

```
docker compose up -d --build
```

The container automatically runs, in order:
1. `migrate` — creates/updates database tables
2. `collectstatic` — gathers CSS into `staticfiles/`, ready for WhiteNoise
   to serve
3. `gunicorn` — starts the actual application server on port 8000

Point your reverse proxy at `http://<server>:8000`.

The `docker-compose.yml` mounts `db.sqlite3`, `media/`, and `staticfiles/`
as volumes so your data survives container rebuilds.

### Create the receptionist/admin account (Docker)

```
docker compose exec web python manage.py createsuperuser
```

## 4. Deploy without Docker (plain VPS)

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export $(cat .env | xargs)   # loads the .env variables into your shell
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
./manage_production.sh
```

For a real deployment, run this under a process manager (systemd,
supervisor, or similar) instead of leaving it in a terminal — systemd is
recommended since it restarts the app automatically if it crashes or the
server reboots.

## 5. Point your reverse proxy at the app

Example Nginx config (adjust paths/domain):

```
server {
    listen 80;
    server_name drporkave.com www.drporkave.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name drporkave.com www.drporkave.com;

    ssl_certificate     /etc/letsencrypt/live/drporkave.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/drporkave.com/privkey.pem;

    location /media/ {
        alias /path/to/project/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Replace `/path/to/project/media/` with the actual path to the `media/`
folder on your server (the same one `docker-compose.yml` mounts as a
volume). This is where photos uploaded through the admin panel (doctor
photo, hero image, before/after cases) are stored — WhiteNoise only
serves `/static/`, so the reverse proxy needs this extra block to serve
`/media/` directly.

Use Certbot (`certbot --nginx`) to obtain a free TLS certificate.

## 6. Load the clinic's schedule on the live site

```
docker compose exec web python manage.py seed_clinic
```

(or the non-Docker equivalent: `python manage.py seed_clinic`)

Then log into `/admin/` and add any known upcoming closed days (e.g.
holidays) under **Schedule exceptions**.

## 7. Moving from SQLite to PostgreSQL later

SQLite is fine for a single clinic with modest traffic. If you outgrow it:

1. Provision a PostgreSQL database.
2. Add `DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DBNAME` to `.env`.
3. Install the Postgres driver: `pip install psycopg2-binary` (add it to
   `requirements.txt` too).
4. Run `python manage.py migrate` again against the new database, then
   `python manage.py seed_clinic`.

No code changes are needed — `clinic/settings_production.py` already
reads `DATABASE_URL` when it's present.

## 8. SEO checklist after going live

- Submit `https://yourdomain.com/sitemap.xml` to Google Search Console.
- Verify `https://yourdomain.com/robots.txt` is reachable and correct.
- Confirm the Open Graph preview looks right (test by pasting the URL into
  a messaging app or using Facebook's Sharing Debugger).
- Once you have a logo, add an `og:image` tag and a favicon (see
  `CONTENT_TODO.md`).

## 9. Backups

`db.sqlite3` is a single file — back it up regularly (e.g. a nightly
cron job that copies it somewhere off-server). If you move to
PostgreSQL, use `pg_dump` on a schedule instead.
