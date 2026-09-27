from datetime import date, datetime, timedelta

from django.db import transaction
from django.utils import timezone

from .models import Appointment, Patient, ScheduleException, ScheduleWeek, WeeklySchedule

SLOT_MINUTES = 30


def persian_weekday(target_date):
    """Convert Python's date.weekday() (Monday=0..Sunday=6) to the
    Persian week used by WeeklySchedule.weekday (Saturday=0..Friday=6).

    Python: Mon=0 Tue=1 Wed=2 Thu=3 Fri=4 Sat=5 Sun=6
    Persian: Sat=0 Sun=1 Mon=2 Tue=3 Wed=4 Thu=5 Fri=6

    This conversion is critical: using date.weekday() directly against
    WeeklySchedule.weekday silently maps every day to the wrong working
    hours (e.g. real Saturdays would be treated as Thursdays).
    """
    return (target_date.weekday() + 2) % 7


def _slots_between(start_time, end_time):
    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)
    while current + timedelta(minutes=SLOT_MINUTES) <= end:
        yield current.time()
        current += timedelta(minutes=SLOT_MINUTES)


def week_start_saturday(target_date):
    return target_date - timedelta(days=(target_date.weekday() + 2) % 7)


def working_windows(target_date):
    exception = ScheduleException.objects.filter(date=target_date).first()
    if exception:
        if exception.kind == ScheduleException.CLOSED:
            return []
        return [(exception.start_time, exception.end_time)]
    specific_week = ScheduleWeek.objects.filter(
        week_start=week_start_saturday(target_date), is_active=True
    ).first()
    if specific_week is not None:
        return list(
            WeeklySchedule.objects.filter(
                schedule_week=specific_week,
                weekday=persian_weekday(target_date),
                is_active=True,
            ).values_list('start_time', 'end_time')
        )
    return list(
        WeeklySchedule.objects.filter(
            schedule_week__isnull=True,
            weekday=persian_weekday(target_date), is_active=True
        ).values_list('start_time', 'end_time')
    )


def available_slots(target_date):
    booked = set(
        Appointment.objects.filter(
            date=target_date, status=Appointment.BOOKED
        ).values_list('start_time', flat=True)
    )
    result = []
    for start, end in working_windows(target_date):
        result.extend(slot for slot in _slots_between(start, end) if slot not in booked)
    result = sorted(result)
    # Do not offer already-passed times on the current Tehran date.
    if target_date == timezone.localdate():
        now = timezone.localtime().time()
        result = [slot for slot in result if slot > now]
    return result


@transaction.atomic
def create_appointment(*, full_name, phone, target_date, start_time, source=Appointment.ONLINE):
    end_time = (datetime.combine(target_date, start_time) + timedelta(minutes=SLOT_MINUTES)).time()
    patient, _ = Patient.objects.get_or_create(phone=phone, defaults={'full_name': full_name})
    if patient.full_name != full_name:
        patient.full_name = full_name
        patient.save(update_fields=['full_name', 'updated_at'])
    return Appointment.objects.create(
        patient=patient,
        date=target_date,
        start_time=start_time,
        end_time=end_time,
        status=Appointment.BOOKED,
        source=source,
    )
