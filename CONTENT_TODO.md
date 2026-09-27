# Content To-Do List

The online appointment picker now uses a Persian (Jalali) calendar in the patient-facing UI; the server still receives the equivalent Gregorian date internally for reliable scheduling.

Everything below is content or business information only you or the
clinic can provide — none of it is a code task.

**You can now upload all photos yourself, directly on the live site —
no need to send files through chat.** See "Uploading your own photos"
in `README.md` for the exact steps (it's a few clicks in the admin
panel: **تصاویر ثابت سایت** for the single photos below, **نمونه‌کارها
(قبل/بعد)** for single-image cases).

## Photos & media

- [x] Placeholder images for doctor, hero, gum disease, and missing-tooth sections are bundled and remain available until real photos are uploaded.
- [ ] Dr. Pourkaveh's professional photo — upload under "تصاویر ثابت
      سایت" → "عکس دکتر". A placeholder shows until you do.
- [ ] Clinic interior/exterior photo for the homepage hero — upload
      under "تصاویر ثابت سایت" → "تصویر هیرو".
- [ ] Two "problem" section photos — upload under "تصاویر ثابت سایت" →
      "تصویر کارت «بیماری لثه»" and "تصویر کارت «بی‌دندانی»".
- [ ] Before/after case photos (~20 total) — add each one under
      "نمونه‌کارها (قبل/بعد)" → "Add". Each case needs a "before" photo
      and a single portfolio photo; the drag-to-compare slider on the homepage
      is now fully working and will reveal one over the other
      automatically once you upload a real pair. Add as many cases as
      you like, in any order — use the "ترتیب نمایش" field to control
      display order, and untick "نمایش در سایت" to hide a case without
      deleting it.
- [x] Clinic logo — the supplied clinic logo is now bundled as `clinic-logo.png` and shown in the header next to the SP logo.
- [x] Favicon — generated from the supplied clinic logo and added to the site.
- [ ] An image for social-media link previews (`og:image`) — ideally the
      logo or a clinic photo, roughly 1200×630px. Not yet added.

## Text content

- [ ] Final, clinic-approved Persian copy for every section (the current
      text was written from your brief as a professional-sounding
      starting point, not final copy).
- [ ] Confirmation of Dr. Pourkaveh's exact academic/publication details
      if you want to state anything more specific than "faculty member
      with academic publications" (no exact numbers were invented, per
      your instructions).
- [ ] Case captions can now be typed directly in the admin when you add
      each case (e.g. "gum graft, 3 months post-op") — totally optional,
      leave blank if you'd rather the photos speak for themselves.

## Business information to confirm

- [ ] **Clinic phone number** — I found two different numbers across the
      previous project files (`09354609333` used in the site, vs.
      `09354409323` on record). I used the latter throughout the final
      site. Please double check which one is correct before launch —
      this is the single most important thing to verify, since it's
      exactly what patients will call to book/cancel.
- [ ] Confirm the clinic address text is exactly right for display:
      "بجنورد، چهارراه مخابرات، خیابان شریعتی جنوبی، ساختمان پزشکان نورا"
- [ ] Confirm the Instagram handle linked in the footer
      (`instagram.com/DR.Sajjad.porkave`) is correct and active.
- [ ] Confirm you're happy with 30-minute default slot length for online
      bookings (the receptionist can still manually create 45-minute
      appointments from the admin panel when needed).

## Before going live

- [ ] A domain name (see `DEPLOYMENT.md`).
- [ ] Decide whether you want a Google Business Profile linked as well —
      not part of this project, but commonly paired with the site for
      the "attract patients from Google" goal.
- [ ] Any known upcoming closed days (holidays, doctor's travel, etc.) so
      they can be entered under **Schedule exceptions** in the admin
      panel before launch.
- [ ] Before deploying, make sure your server's reverse proxy is
      configured to serve `/media/` (see the updated Nginx example in
      `DEPLOYMENT.md`) — this is what makes uploaded photos visible on
      the live site, separate from the site's own static design files.

## Explicitly deferred (per your instructions, not forgotten)

- [ ] SMS appointment reminders — architecture is ready, integration is
      intentionally not built yet.
- [ ] An "About Us" page — intentionally excluded, as requested.

