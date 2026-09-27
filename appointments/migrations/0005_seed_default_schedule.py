from django.db import migrations


def seed_default_schedule(apps, schema_editor):
    WeeklySchedule = apps.get_model('appointments', 'WeeklySchedule')

    # The booking system needs a default schedule on a fresh installation.
    # Do not overwrite anything if a default schedule has already been created.
    if WeeklySchedule.objects.filter(schedule_week__isnull=True).exists():
        return

    schedule = {
        0: [('16:00', '20:00')],  # Saturday
        1: [('16:00', '20:00')],  # Sunday
        2: [('16:00', '20:00')],  # Monday
        3: [('16:00', '20:00')],  # Tuesday
        4: [('16:00', '20:00')],  # Wednesday
        5: [('10:00', '13:00'), ('16:00', '20:00')],  # Thursday
        6: [],  # Friday
    }

    for weekday, windows in schedule.items():
        for start, end in windows:
            WeeklySchedule.objects.create(
                weekday=weekday,
                start_time=start,
                end_time=end,
                is_active=True,
            )


def remove_seeded_default_schedule(apps, schema_editor):
    WeeklySchedule = apps.get_model('appointments', 'WeeklySchedule')
    WeeklySchedule.objects.filter(schedule_week__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('appointments', '0004_flexible_weekly_schedule'),
    ]

    operations = [
        migrations.RunPython(seed_default_schedule, remove_seeded_default_schedule),
    ]
