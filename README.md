# Dr. Sajjad Pourkaveh — Clinic Website

A Django website for Dr. Sajjad Pourkaveh's periodontics clinic in Bojnurd:
a public homepage, an online appointment booking page, and a Django admin
panel for the receptionist.

This guide assumes you have never run a Django project before.

## 1. Install Python

You need Python 3.11 or newer. Check with:

```
python3 --version
```

If you don't have it, download it from https://www.python.org/downloads/.

## 2. Open a terminal in the project folder

Unzip this project, then open a terminal (Command Prompt / Terminal app)
inside the unzipped folder — the one that contains `manage.py`.

## 3. Create a virtual environment

This keeps this project's Python packages separate from everything else
on your computer.

```
python3 -m venv .venv
```

Activate it:

- **Windows:** `.venv\Scripts\activate`
- **macOS / Linux:** `source .venv/bin/activate`

You'll know it worked if your terminal prompt now starts with `(.venv)`.
Run every command below inside this activated environment.

## 4. Install the required packages

```
pip install -r requirements.txt
```

## 5. Set up the database

This creates a local `db.sqlite3` file with all the tables the site needs.

```
python manage.py migrate
```

## 6. Load the clinic's default weekly schedule

```
python manage.py seed_clinic
```

This sets up:
- Saturday–Wednesday: 16:00–20:00
- Thursday: 10:00–13:00 and 16:00–20:00
- Friday: closed

You (or the receptionist) can change this later from the admin panel.

## 7. Create a receptionist/admin login

```
python manage.py createsuperuser
```

It will ask for a username, email (optional), and password. Remember these
— this is how the receptionist logs into the admin panel.

## 8. Run the website

```
python manage.py runserver
```

Now open your browser to:

- **Homepage:** http://127.0.0.1:8000/
- **Booking page:** http://127.0.0.1:8000/booking/
- **Admin panel:** http://127.0.0.1:8000/admin/ (log in with the account
  from step 7)

Press `Ctrl+C` in the terminal to stop the server.

## Uploading your own photos (no developer needed)

You don't need to send me photo files anymore. Once you're logged into
the admin panel (http://127.0.0.1:8000/admin/ locally, or your real
domain + `/admin/` once deployed):

**Single photos (hero background, doctor photo, the two problem-card
images):**
1. Click **"تصاویر ثابت سایت"**.
2. Click on the row you want to change (e.g. "عکس دکتر").
3. Click **"Choose File"** next to **تصویر**, pick the photo from your
   computer or phone, and click **Save**.
4. Refresh the homepage — the new photo is live immediately.

If a slot has no photo uploaded yet, the site automatically shows an
elegant placeholder instead of a broken image, so it's always safe to
leave some empty for now.

**Before/after cases:**
1. Click **"نمونه‌کارها (قبل/بعد)"**.
2. Click **"ADD نمونه کار (قبل/بعد)"** in the top right.
3. Upload the "before" photo and the "after" photo, optionally add a
   short caption, and click **Save**.
4. It appears immediately on the homepage with a working drag-to-compare
   slider. Add as many as you like — untick "نمایش در سایت" on any case
   you want to hide without deleting it.

Get patient consent before publishing any before/after photo, and make
sure the images don't reveal identifying details (per your own note in
`CONTENT_TODO.md`).

## What the receptionist can do in the admin panel

- **Appointments** — see all booked appointments, create one manually
  (search for an existing patient or add a new one first under
  "Patients"), or mark one as cancelled/completed/no-show.
- **Patients** — search and view patient records.
- **Weekly schedules** — the clinic's normal recurring working hours.
- **Schedule exceptions** — close a specific date entirely, or give it
  different hours than usual (e.g. a holiday with shortened hours).

A manually created appointment automatically blocks that time slot from
being booked online, and vice versa.

## Running the automated tests

To check that the booking logic still works correctly after any change:

```
python manage.py test appointments
```

## What's still missing before this goes live

See `CONTENT_TODO.md` for content you need to supply, and
`DEPLOYMENT.md` for how to put this on a real server with a domain name.

## اضافه کردن دستی نمونه‌کارهای قبل/بعد

برای اضافه کردن عکس‌های واقعی نمونه‌کار، نیازی به Admin یا ارسال فایل برای توسعه‌دهنده نیست.

1. وارد پوشه `appointments/static/appointments/img/cases/` شو.
2. برای هر درمان، دو عکس با این الگو قرار بده:
   - `01-before.jpg`
   - `01-after.jpg`
3. نمونه‌کار بعدی را با `02-before.jpg` و `02-after.jpg` اضافه کن.
4. عدد اول ترتیب نمایش را مشخص می‌کند.
5. فرمت‌های JPG، JPEG، PNG و WEBP پشتیبانی می‌شوند.
6. اگر کپشن می‌خواهی، یک فایل متنی هم کنار عکس‌ها بگذار؛ مثلاً `01-caption.txt` و متن کپشن را داخل آن بنویس.

وقتی پروژه را روی هاست Deploy می‌کنی، عکس‌هایی که داخل این پوشه هستند نیز همراه پروژه نمایش داده می‌شوند.

**نکته:** عکس‌های قبل و بعد را بدون تغییر نام‌گذاری کن؛ فقط بخش `-before` و `-after` باید متفاوت باشد.
