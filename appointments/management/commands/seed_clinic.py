from django.core.management.base import BaseCommand

from appointments.models import ScheduleWeek, SiteContent, SiteImage, WeeklySchedule


class Command(BaseCommand):
    help = 'Create the default clinic weekly schedule and the editable image slots.'

    def handle(self, *args, **kwargs):
        ScheduleWeek.objects.all().delete()
        WeeklySchedule.objects.all().delete()
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
                WeeklySchedule.objects.create(weekday=weekday, start_time=start, end_time=end, is_active=True)
        self.stdout.write(self.style.SUCCESS('Default clinic schedule created.'))

        for key, _label in SiteImage.KEY_CHOICES:
            SiteImage.objects.get_or_create(key=key)
        self.stdout.write(self.style.SUCCESS(
            'Image slots ready in the admin panel under \"تصاویر ثابت سایت\".'
        ))

        defaults = {
            SiteContent.ABOUT: {
                'eyebrow': 'آشنایی با پزشک',
                'title': 'دکتر سجاد پورکاوه',
                'body': 'فارغ‌التحصیل از دانشگاه‌های مشهد و تبریز\nاستادیار دانشکده دندانپزشکی بجنورد',
            },
            SiteContent.EDUCATION: {
                'eyebrow': 'دانش و تجربه',
                'title': 'درمان تخصصی، بر پایه‌ی تشخیص دقیق',
                'body': 'محتوای آموزشی سایت در این بخش قرار می‌گیرد تا بیمار پیش از مراجعه، شناخت روشن‌تری از بیماری‌های لثه، ایمپلنت و روند درمان داشته باشد.',
                'button_text': 'مشاهده مطالب آموزشی',
                'button_url': '#contact',
            },
        }
        for key, values in defaults.items():
            SiteContent.objects.get_or_create(key=key, defaults=values)
        self.stdout.write(self.style.SUCCESS('Editable About and Education content is ready in the admin panel under \"محتوای سایت\".'))
