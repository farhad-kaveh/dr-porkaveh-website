# QA Report

## Summary

All three ZIP archives were merged into one Django project. Several real
bugs were found and fixed (see "Bugs found and fixed" below). All 24
requested checks pass — 17 of them are covered by an automated test suite
(`appointments/tests.py`, 19 tests, all passing); the rest are
infrastructure/manual checks documented below.

## Bugs found and fixed

1. **Weekday mismatch (would have broken almost all bookings).**
   `WeeklySchedule.weekday` uses a Persian week (Saturday=0 .. Friday=6),
   matching the receptionist-facing admin and the seed data. But
   `services.py` computed availability using Python's native
   `date.weekday()` (Monday=0 .. Sunday=6). Every date would have resolved
   against the wrong day's schedule — e.g. real Saturdays would have used
   Thursday's hours. Fixed with an explicit `persian_weekday()` conversion
   function in `services.py`, with a comment explaining why it's needed
   and a dedicated test (`WeekdayConversionTests`) pinning known dates to
   their expected Persian weekday.

2. **Patient data exposed on the public homepage.** The root URL (`/`)
   rendered a "dashboard" template listing today's booked patients' full
   names and phone numbers, with no login required. This was a leftover
   developer test page from phase 1 that had not been replaced when phase
   2's real public homepage was built. Fixed by renaming the view to
   `home`, pointing `/` at the real (patient-data-free) marketing
   homepage from phase 2, and confirming via test
   (`test_homepage_loads`) that the homepage response never contains
   patient-related text.

3. **No database migrations existed.** Only an empty
   `migrations/__init__.py` was present in every phase. The project could
   not have started from a clean install as shipped. Generated
   `0001_initial.py` from the existing (sound) models and verified a full
   clean-install cycle (`migrate` → `seed_clinic` → run).

4. **Broken production settings.** `config/settings_production.py` did
   `from .settings import *`, but no `config/settings.py` existed
   anywhere in any phase — this would have crashed immediately on
   startup. It also assumed the project package was named `config`, while
   the actual Django project (built in phase 1) is named `clinic`, so
   `Procfile` and `manage_production.sh` pointed at a WSGI module that
   doesn't exist. Fixed by creating `clinic/settings_production.py` that
   correctly imports from `clinic/settings.py`, and correcting
   `Procfile`/`manage_production.sh`/`Dockerfile` to reference
   `clinic.wsgi`. Also added a hard failure if `DJANGO_SECRET_KEY` isn't
   set, so a misconfigured deploy can't silently fall back to the
   insecure dev key.

5. **`robots.txt` and `sitemap.xml` templates existed but were never
   wired to a URL.** Phase 3's `urls.py` imported `TemplateView` but
   never used it. Fixed by adding both routes in `appointments/urls.py`.

6. **Invalid template syntax in the SEO metadata.** `{{ self.title }}`
   in `base.html` is Jinja2 syntax, not valid in Django templates — it
   would have silently rendered as empty, leaving the `og:title` tag
   blank. Fixed using a proper `{% block og_title %}` pattern that each
   page template overrides alongside `{% block title %}`.

7. **Static-file storage would have broken local development.** WhiteNoise's
   manifest storage (`CompressedManifestStaticFilesStorage`) requires
   `collectstatic` to have already run, or every `{% static %}` tag
   raises an error. It's only enabled in `settings_production.py`; base
   `settings.py` (used for local dev) uses Django's plain static file
   handling, which works with `runserver` immediately after a clean
   install.

8. **Missing clickjacking protection.** `django.middleware.clickjacking.
   XFrameOptionsMiddleware` was absent from `MIDDLEWARE` (flagged by
   Django's own `manage.py check --deploy`). Added.

9. **Inconsistent clinic phone number.** The footer and the structured
   data (JSON-LD) both showed `09354609333`. This differs from the number
   on record for the clinic, `09354409323`. I've used the number on
   record throughout the site — **please double-check this number is
   correct before launch** (see `CONTENT_TODO.md`).

## Frontend redesign (second pass)

A new visual design (dark/gold, single-page marketing style) was supplied
separately as static HTML/CSS/JS and integrated into the Django project:

- The new header, navigation, hero, problem cards, services strip,
  case-study grid, doctor section, education section, final CTA, and
  footer now form the site's shared visual language (`base.html` +
  `home.html`).
- The booking and confirmation pages were re-skinned to match (same
  color system, buttons, and card style) so the whole site feels
  consistent — but their actual form fields, field names, validation,
  CSRF handling, and the JavaScript that fetches available slots from
  `/api/slots/` were **not changed**. All 19 automated tests still pass
  unmodified, confirming the booking logic itself was untouched.
- All image references in the new CSS (`hero-clinic.jpg`,
  `problem-gum.jpg`, `problem-implant.jpg`, `case-01/02/03.jpg`,
  `doctor.jpg`) currently point at generated placeholder images (dark/
  gold, clearly labeled "PLACEHOLDER — REPLACE WITH REAL PHOTO") so the
  site never shows a broken image while real photos are pending — see
  `CONTENT_TODO.md`.
- Re-verified `collectstatic` under production settings: WhiteNoise
  correctly rewrites every `url(...)` reference inside the CSS to the
  hashed filename of the corresponding image, confirmed by inspecting
  the generated `style.<hash>.css`.
- **Note on the before/after slider:** the case cards include a
  drag-to-compare slider (range input), but as shipped in the new
  frontend it only sets a CSS variable (`--split`) that nothing currently
  reads — the supplied CSS doesn't yet define the clip-path/mask that
  would make the slider visually do anything. This isn't something I
  introduced or need to silently "fix": the frontend's own JS comment
  already marks it as a placeholder ("visual prototype... replace each
  case background with real before/after assets when available"). It's
  listed in `CONTENT_TODO.md` as something to revisit once you have
  real paired before/after photos for each case.

## Automated tests (`python manage.py test appointments`)

19 tests, all passing:

- Weekday conversion is correct for all 7 days (pinned to real calendar
  dates).
- Saturday, Wednesday, and both Thursday windows (10–13 and 16–20) return
  the expected slots.
- Friday returns no slots.
- A `ScheduleException` (closed or custom hours) correctly overrides the
  normal weekly schedule, both for a normally-open day and a
  normally-closed day.
- Homepage returns 200 and never contains patient-identifying text.
- Booking page returns 200.
- A patient can book an available slot; the appointment is created with
  the correct date/time/status/source.
- A patient cannot book an already-occupied slot (clear error message,
  no duplicate appointment created).
- Submitting without a name, or without a phone number, is rejected and
  creates no appointment.
- The public slots API correctly returns an empty list for Friday and for
  a day closed via an exception.
- A logged-in admin/receptionist can see appointments in the admin
  change list.
- A manually created (reception-source) appointment blocks that slot from
  online booking.
- A receptionist can close a normally-open day via `ScheduleException`,
  and it correctly becomes unavailable.

## Full checklist against the 24 requested items

| # | Item | Result | How verified |
|---|------|--------|---------------|
| 1 | Homepage loads | ✅ Pass | Automated test + manual `curl` |
| 2 | Booking page loads | ✅ Pass | Automated test + manual `curl` |
| 3 | Saturday booking works | ✅ Pass | Automated test + manual `curl` |
| 4 | Wednesday booking works | ✅ Pass | Automated test |
| 5 | Thursday 10–13 works | ✅ Pass | Automated test |
| 6 | Thursday 16–20 works | ✅ Pass | Automated test |
| 7 | Friday has no availability | ✅ Pass | Automated test + manual `curl` |
| 8 | Closed day has no availability | ✅ Pass | Automated test |
| 9 | Patient can select an available slot | ✅ Pass | Automated test + manual end-to-end HTTP POST with real CSRF token |
| 10 | Patient cannot book an occupied slot | ✅ Pass | Automated test |
| 11 | Cannot submit without name | ✅ Pass | Automated test |
| 12 | Cannot submit without phone | ✅ Pass | Automated test |
| 13 | Successful booking creates an appointment | ✅ Pass | Automated test |
| 14 | Confirmation page appears | ✅ Pass | Automated test + manual end-to-end |
| 15 | Receptionist/admin can see the appointment | ✅ Pass | Automated test |
| 16 | Receptionist can manually create an appointment | ✅ Pass | Verified via Django admin (autocomplete-enabled Patient field) |
| 17 | Manual appointment blocks online booking | ✅ Pass | Automated test |
| 18 | Receptionist can close a day | ✅ Pass | Automated test |
| 19 | Closed day blocks online booking | ✅ Pass | Automated test (same mechanism as #8/#18) |
| 20 | Application starts from a clean installation | ✅ Pass | Full clean-install cycle run manually: fresh copy → `migrate` → `seed_clinic` → `createsuperuser` → `runserver`, all pages loaded |
| 21 | Production settings work | ✅ Pass | `DJANGO_SETTINGS_MODULE=clinic.settings_production` loads correctly with env vars set; fails loudly and clearly if `DJANGO_SECRET_KEY` is missing; `manage.py check --deploy` run and remaining warning is only about using a short test secret key |
| 22 | Static files work | ✅ Pass | `collectstatic` under production settings succeeds; hashed filenames generated by WhiteNoise; CSS loads correctly |
| 23 | `robots.txt` works | ✅ Pass | Manual `curl`, correct content and content-type |
| 24 | `sitemap.xml` works | ✅ Pass | Manual `curl`, correct content and content-type |

## Self-service photo management (third pass)

Since sending every photo through chat wasn't practical, a proper
content-management layer was added so the clinic owner can upload and
replace photos directly from the Django admin panel — no developer
involvement needed going forward:

- **`SiteImage` model**: 4 fixed, pre-created slots (hero background,
  doctor photo, and the two problem-card images) editable from
  **"تصاویر ثابت سایت"** in the admin. Each row shows a live thumbnail
  preview. If a slot has no image uploaded, the homepage automatically
  falls back to the existing placeholder graphic — the site can never
  show a broken image.
- **`CaseStudy` model**: an unlimited, add-as-needed list of before/after
  cases under **"نمونه‌کارها (قبل/بعد)"**, each with its own before
  photo, after photo, optional caption, a publish/unpublish toggle
  (`is_published`), and a manual ordering field. Unpublishing hides a
  case from the site without deleting it.
- **The before/after slider now actually works.** Previously (see the
  frontend redesign notes above) the drag-to-compare slider only set an
  unused CSS variable. Now that real paired before/after images exist
  per case, the CSS was extended with a `clip-path` rule that the same
  slider variable drives, so dragging the handle genuinely reveals the
  "after" photo over the "before" photo. This only activates for real
  uploaded cases; the placeholder cards shown before any case exists
  have the slider disabled (there's nothing meaningful to compare yet).
- `seed_clinic` now also creates the 4 empty `SiteImage` rows (in
  addition to the weekly schedule it already created), so a fresh
  install has ready-to-click rows in the admin rather than requiring
  someone to know the exact internal key to type in.
- Verified end-to-end over real HTTP: logged into `/admin/`, uploaded a
  test hero image and a test before/after case through the actual admin
  forms (not just the ORM), and confirmed both appeared correctly on the
  live homepage — including the case caption and the real `/media/...`
  URLs.
- Re-ran `collectstatic` and `check --deploy` under production settings
  after these changes — both succeed. Added `Pillow` to
  `requirements.txt` (required by Django's `ImageField`).
- Production media serving: WhiteNoise only serves `/static/`, not
  `/media/`, so `DEPLOYMENT.md` now includes the required Nginx
  `location /media/` block pointing at the mounted `media/` folder.
  Local development serves `/media/` automatically via Django when
  `DEBUG=True`.
- 4 new automated tests added (23 total, all passing): homepage falls
  back to the placeholder when no image is uploaded, an uploaded
  `SiteImage` actually renders on the homepage, the homepage falls back
  to the 3 static placeholder cases when no `CaseStudy` exists yet, and
  only published case studies render (with their captions) when they do
  exist.

## What remains to be done

These are not code defects — they're real-world steps that only you or
the clinic can complete:

- **Confirm the correct clinic phone number** (see bug #9 above) before
  launch.
- Replace all image/photo placeholders — see `CONTENT_TODO.md`.
- Get final approved marketing copy reviewed (current text is
  placeholder-quality Persian copy written from your brief, not
  clinic-approved final copy).
- Register a domain and complete the steps in `DEPLOYMENT.md`.
- Add a favicon and an `og:image` once a logo exists.
- SMS reminders were intentionally **not** implemented, per your
  instructions — the architecture (separate `Appointment.source` field,
  clean `services.py` boundary) is left ready for it to be added later
  without restructuring the app.
- No automated browser/visual (screenshot) testing was performed — only
  HTTP-level and database-level testing. A manual look at the site on an
  actual phone is still worth doing before launch, especially the RTL
  layout and the date picker on iOS Safari.
- Load/performance testing was not performed — unnecessary at this stage
  for a single-clinic booking site, but worth revisiting if this becomes
  a multi-clinic product.
