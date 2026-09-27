"""
Automated tests for the booking system.

Run with:  python manage.py test appointments
"""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Appointment, Patient, ScheduleException, ScheduleWeek, WeeklySchedule
from .services import available_slots, create_appointment, persian_weekday, week_start_saturday


def _next_weekday(persian_day):
    """Return the next date (today included) whose Persian weekday matches
    persian_day (0=Saturday .. 6=Friday)."""
    d = date.today()
    for _ in range(8):
        if persian_weekday(d) == persian_day:
            return d
        d += timedelta(days=1)
    raise AssertionError('could not find matching weekday')


class WeekdayConversionTests(TestCase):
    def test_known_dates_map_to_expected_persian_weekday(self):
        # 2026-08-29 is a Saturday.
        self.assertEqual(persian_weekday(date(2026, 8, 29)), 0)  # Saturday
        self.assertEqual(persian_weekday(date(2026, 8, 30)), 1)  # Sunday
        self.assertEqual(persian_weekday(date(2026, 8, 31)), 2)  # Monday
        self.assertEqual(persian_weekday(date(2026, 9, 1)), 3)   # Tuesday
        self.assertEqual(persian_weekday(date(2026, 9, 2)), 4)   # Wednesday
        self.assertEqual(persian_weekday(date(2026, 9, 3)), 5)   # Thursday
        self.assertEqual(persian_weekday(date(2026, 9, 4)), 6)   # Friday


class ScheduleFixtureMixin:
    """Creates the clinic's standard weekly schedule (same as seed_clinic)."""

    def setUp(self):
        WeeklySchedule.objects.all().delete()
        windows = {
            0: [('16:00', '20:00')],  # Saturday
            1: [('16:00', '20:00')],  # Sunday
            2: [('16:00', '20:00')],  # Monday
            3: [('16:00', '20:00')],  # Tuesday
            4: [('16:00', '20:00')],  # Wednesday
            5: [('10:00', '13:00'), ('16:00', '20:00')],  # Thursday
            6: [],  # Friday: closed
        }
        for weekday, ranges in windows.items():
            for start, end in ranges:
                WeeklySchedule.objects.create(
                    weekday=weekday, start_time=start, end_time=end, is_active=True
                )


class AvailabilityTests(ScheduleFixtureMixin, TestCase):
    def test_saturday_has_evening_slots(self):
        from datetime import time
        d = _next_weekday(0)
        slots = available_slots(d)
        self.assertIn(time(16, 0), slots)

    def test_wednesday_has_evening_slots(self):
        d = _next_weekday(4)
        slots = available_slots(d)
        self.assertTrue(len(slots) > 0)
        self.assertEqual(slots[0].strftime('%H:%M'), '16:00')

    def test_thursday_morning_slots(self):
        d = _next_weekday(5)
        slots = available_slots(d)
        times = [s.strftime('%H:%M') for s in slots]
        self.assertIn('10:00', times)

    def test_thursday_evening_slots(self):
        d = _next_weekday(5)
        slots = available_slots(d)
        times = [s.strftime('%H:%M') for s in slots]
        self.assertIn('16:00', times)

    def test_friday_has_no_slots(self):
        d = _next_weekday(6)
        self.assertEqual(available_slots(d), [])

    def test_closed_exception_overrides_normal_schedule(self):
        d = _next_weekday(0)  # normally open Saturday
        ScheduleException.objects.create(date=d, kind=ScheduleException.CLOSED)
        self.assertEqual(available_slots(d), [])

    def test_custom_exception_overrides_normal_schedule(self):
        d = _next_weekday(6)  # normally closed Friday
        ScheduleException.objects.create(
            date=d, kind=ScheduleException.CUSTOM, start_time='10:00', end_time='11:00'
        )
        times = [s.strftime('%H:%M') for s in available_slots(d)]
        self.assertEqual(times, ['10:00', '10:30'])


class FlexibleWeeklyScheduleTests(ScheduleFixtureMixin, TestCase):
    def test_specific_week_overrides_recurring_schedule(self):
        from datetime import time
        target = _next_weekday(0)
        week = ScheduleWeek.objects.create(week_start=week_start_saturday(target))
        WeeklySchedule.objects.create(
            schedule_week=week, weekday=0, start_time='18:00', end_time='19:00', is_active=True
        )
        times = [slot.strftime('%H:%M') for slot in available_slots(target)]
        self.assertEqual(times, ['18:00', '18:30'])

    def test_specific_week_can_close_a_normally_open_day(self):
        target = _next_weekday(0)
        ScheduleWeek.objects.create(week_start=week_start_saturday(target))
        self.assertEqual(available_slots(target), [])

    def test_specific_week_can_change_two_windows(self):
        target = _next_weekday(5)
        week = ScheduleWeek.objects.create(week_start=week_start_saturday(target))
        WeeklySchedule.objects.create(schedule_week=week, weekday=5, start_time='09:00', end_time='11:00', is_active=True)
        WeeklySchedule.objects.create(schedule_week=week, weekday=5, start_time='17:00', end_time='19:00', is_active=True)
        times = [slot.strftime('%H:%M') for slot in available_slots(target)]
        self.assertEqual(times[0], '09:00')
        self.assertEqual(times[-1], '18:30')


class BookingFlowTests(ScheduleFixtureMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # The public homepage must never show patient data.
        self.assertNotContains(response, 'شماره موبایل')

    def test_booking_page_loads(self):
        response = self.client.get(reverse('booking'))
        self.assertEqual(response.status_code, 200)

    def test_patient_can_select_and_book_an_available_slot(self):
        d = _next_weekday(0)
        response = self.client.post(reverse('booking'), {
            'full_name': 'علی رضایی',
            'phone': '09121234567',
            'date': d.isoformat(),
            'slot': '16:00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'نوبت شما ثبت شد')
        self.assertEqual(Appointment.objects.count(), 1)
        appointment = Appointment.objects.get()
        self.assertEqual(appointment.date, d)
        self.assertEqual(appointment.start_time.strftime('%H:%M'), '16:00')
        self.assertEqual(appointment.status, Appointment.BOOKED)
        self.assertEqual(appointment.source, Appointment.ONLINE)

    def test_patient_cannot_book_an_occupied_slot(self):
        from datetime import time
        d = _next_weekday(0)
        create_appointment(full_name='بیمار اول', phone='09121111111', target_date=d, start_time=time(16, 0))
        response = self.client.post(reverse('booking'), {
            'full_name': 'بیمار دوم',
            'phone': '09122222222',
            'date': d.isoformat(),
            'slot': '16:00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'این زمان دیگر آزاد نیست')
        self.assertEqual(Appointment.objects.count(), 1)

    def test_cannot_submit_without_name(self):
        d = _next_weekday(0)
        response = self.client.post(reverse('booking'), {
            'full_name': '',
            'phone': '09121234567',
            'date': d.isoformat(),
            'slot': '16:00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_cannot_submit_without_phone(self):
        d = _next_weekday(0)
        response = self.client.post(reverse('booking'), {
            'full_name': 'علی رضایی',
            'phone': '',
            'date': d.isoformat(),
            'slot': '16:00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_friday_has_no_availability_via_api(self):
        d = _next_weekday(6)
        response = self.client.get(reverse('slots_api'), {'date': d.isoformat()})
        self.assertEqual(response.json()['slots'], [])

    def test_closed_day_has_no_availability_via_api(self):
        d = _next_weekday(0)
        ScheduleException.objects.create(date=d, kind=ScheduleException.CLOSED)
        response = self.client.get(reverse('slots_api'), {'date': d.isoformat()})
        self.assertEqual(response.json()['slots'], [])


class ReceptionistAdminTests(ScheduleFixtureMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        User = get_user_model()
        self.staff_user = User.objects.create_superuser(
            username='reception', email='reception@example.com', password='test-pass-123'
        )
        self.client.login(username='reception', password='test-pass-123')

    def test_admin_can_see_appointments(self):
        from datetime import time
        d = _next_weekday(0)
        create_appointment(full_name='بیمار تستی', phone='09121234567', target_date=d, start_time=time(16, 0))
        response = self.client.get(reverse('admin:appointments_appointment_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'بیمار تستی')

    def test_receptionist_can_open_tomorrows_schedule_chart(self):
        d = date.today() + timedelta(days=1)
        response = self.client.get(reverse('admin:appointments_appointment_schedule'), {'date': d.isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'تقویم نوبت‌ها')

    def test_manual_appointment_blocks_online_booking(self):
        from datetime import time
        d = _next_weekday(0)
        patient = Patient.objects.create(full_name='بیمار منشی', phone='09129876543')
        Appointment.objects.create(
            patient=patient, date=d, start_time='16:00', end_time='16:45',
            status=Appointment.BOOKED, source=Appointment.RECEPTION,
        )
        self.assertNotIn(time(16, 0), available_slots(d))
        response = Client().post(reverse('booking'), {
            'full_name': 'بیمار آنلاین',
            'phone': '09121112222',
            'date': d.isoformat(),
            'slot': '16:00',
        })
        self.assertContains(response, 'این زمان دیگر آزاد نیست')

    def test_receptionist_can_close_a_day(self):
        d = _next_weekday(1)
        self.assertTrue(len(available_slots(d)) > 0)
        ScheduleException.objects.create(date=d, kind=ScheduleException.CLOSED, note='تعطیلی موردی')
        self.assertEqual(available_slots(d), [])


class SiteImageAndCaseStudyTests(ScheduleFixtureMixin, TestCase):
    """Covers the self-service photo/case-study manager added for the
    clinic owner to upload content without developer help."""

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_homepage_uses_placeholder_when_no_image_uploaded(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # No inline background-image override -> the linked stylesheet's
        # own placeholder background-image is what actually renders.
        self.assertNotContains(response, 'class="hero-image" style=')

    def test_homepage_uses_uploaded_site_image_when_present(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        from .models import SiteImage

        buf = io.BytesIO()
        Image.new('RGB', (10, 10), 'white').save(buf, format='JPEG')
        buf.seek(0)
        SiteImage.objects.create(
            key=SiteImage.HERO,
            image=SimpleUploadedFile('hero.jpg', buf.read(), content_type='image/jpeg'),
        )
        response = self.client.get(reverse('home'))
        self.assertContains(response, '/media/site/hero')

    def test_homepage_shows_placeholder_cases_when_none_published(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'نمونه‌کارهای واقعی درمان در این بخش قرار می‌گیرند.')

    def test_homepage_shows_published_case_studies(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        from .models import CaseStudy

        def _img(name):
            buf = io.BytesIO()
            Image.new('RGB', (10, 10), 'white').save(buf, format='JPEG')
            buf.seek(0)
            return SimpleUploadedFile(name, buf.read(), content_type='image/jpeg')

        CaseStudy.objects.create(image=_img('case1.jpg'), caption='مورد اول', is_published=True)
        CaseStudy.objects.create(image=_img('case2.jpg'), is_published=False)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'مورد اول')
        self.assertContains(response, 'case-single-image')
        content = response.content.decode()
        self.assertEqual(content.count('case-caption'), 1)  # only the published one renders
