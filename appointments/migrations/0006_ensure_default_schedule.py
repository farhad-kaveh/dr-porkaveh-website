from django.db import migrations


def ensure_default_schedule(apps, schema_editor):
    WeeklySchedule = apps.get_model('appointments', 'WeeklySchedule')

    # This migration is intentionally idempotent. It repairs installations
    # where the previous seed migration was already marked applied but the
    # default schedule is missing.
    if WeeklySchedule.objects.filter(schedule_week__isnull=True, is_active=True).exists():
        return

    schedule = {
        0: [('16:00', '20:00')],
        1: [('16:00', '20:00')],
        2: [('16:00', '20:00')],
        3: [('16:00', '20:00')],
        4: [('16:00', '20:00')],
        5: [('10:00', '13:00'), ('16:00', '20:00')],
        6: [],
    }

    for weekday, windows in schedule.items():
        for start, end in windows:
            WeeklySchedule.objects.create(
                weekday=weekday,
                start_time=start,
                end_time=end,
                is_active=True,
            )


class Migration(migrations.Migration):
    dependencies = [('appointments', '0005_seed_default_schedule')]
    operations = [migrations.RunPython(ensure_default_schedule, migrations.RunPython.noop)]
