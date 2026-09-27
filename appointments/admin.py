from datetime import date, datetime, timedelta

from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html

from .models import (
    Appointment,
    CaseStudy,
    Patient,
    ScheduleException,
    ScheduleWeek,
    SiteImage,
    SiteContent,
    WeeklySchedule,
)
from .services import _slots_between, persian_weekday, week_start_saturday, working_windows
from .jalali import jalali_date_string


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'created_at')
    search_fields = ('full_name', 'phone')


@admin.register(WeeklySchedule)
class WeeklyScheduleAdmin(admin.ModelAdmin):
    list_display = ('week_label', 'weekday', 'start_time', 'end_time', 'is_active')
    list_filter = ('weekday', 'is_active', 'schedule_week')
    change_list_template = 'admin/appointments/weekly_schedule/change_list.html'

    @admin.display(description='هفته')
    def week_label(self, obj):
        return obj.schedule_week.week_start if obj.schedule_week else 'برنامه پیش‌فرض'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('planner/', self.admin_site.admin_view(self.planner_view), name='appointments_weeklyschedule_planner'),
        ]
        return custom + urls

    def planner_view(self, request):
        today = date.today()
        default_week = week_start_saturday(today)
        raw_week = request.POST.get('week_start') or request.GET.get('week')
        try:
            selected_week = date.fromisoformat(raw_week) if raw_week else default_week
        except ValueError:
            selected_week = default_week
        selected_week = week_start_saturday(selected_week)

        if request.method == 'POST' and request.POST.get('action') == 'save':
            with transaction.atomic():
                week, _ = ScheduleWeek.objects.get_or_create(week_start=selected_week)
                week.is_active = True
                week.note = request.POST.get('note', '').strip()
                week.save(update_fields=['is_active', 'note'])
                WeeklySchedule.objects.filter(schedule_week=week).delete()

                for weekday in range(7):
                    for index in (1, 2):
                        start = request.POST.get(f'day_{weekday}_start_{index}', '').strip()
                        end = request.POST.get(f'day_{weekday}_end_{index}', '').strip()
                        active = request.POST.get(f'day_{weekday}_active_{index}') == 'on'
                        if not active:
                            continue
                        if not start and not end:
                            continue
                        if not start or not end:
                            messages.error(request, f'برای {dict(WeeklySchedule.DAYS)[weekday]}، شروع و پایان هر بازه باید کامل باشد.')
                            return redirect(request.path + f'?week={selected_week.isoformat()}')
                        try:
                            start_t = datetime.strptime(start, '%H:%M').time()
                            end_t = datetime.strptime(end, '%H:%M').time()
                        except ValueError:
                            messages.error(request, 'فرمت ساعت باید HH:MM باشد.')
                            return redirect(request.path + f'?week={selected_week.isoformat()}')
                        if end_t <= start_t:
                            messages.error(request, f'برای {dict(WeeklySchedule.DAYS)[weekday]}، ساعت پایان باید بعد از شروع باشد.')
                            return redirect(request.path + f'?week={selected_week.isoformat()}')
                        WeeklySchedule.objects.create(
                            schedule_week=week,
                            weekday=weekday,
                            start_time=start_t,
                            end_time=end_t,
                            is_active=True,
                        )
            messages.success(request, 'برنامه کاری این هفته با موفقیت ذخیره شد.')
            return redirect(request.path + f'?week={selected_week.isoformat()}')

        specific_week = ScheduleWeek.objects.filter(week_start=selected_week, is_active=True).first()
        source_rows = WeeklySchedule.objects.filter(schedule_week=specific_week) if specific_week else WeeklySchedule.objects.filter(schedule_week__isnull=True, is_active=True)
        grouped = {day: [] for day in range(7)}
        for row in source_rows.order_by('weekday', 'start_time'):
            grouped[row.weekday].append(row)

        days = []
        for weekday, label in WeeklySchedule.DAYS:
            rows = grouped[weekday]
            windows = []
            for index in (0, 1):
                row = rows[index] if index < len(rows) else None
                windows.append({
                    'start': row.start_time.strftime('%H:%M') if row else '',
                    'end': row.end_time.strftime('%H:%M') if row else '',
                    'active': bool(row),
                })
            days.append({'weekday': weekday, 'label': label, 'windows': windows})

        previous_week = selected_week - timedelta(days=7)
        next_week = selected_week + timedelta(days=7)
        context = {
            **self.admin_site.each_context(request),
            'title': 'تنظیم ساعات کاری هفته',
            'opts': self.model._meta,
            'selected_week': selected_week,
            'days': days,
            'note': specific_week.note if specific_week else '',
            'is_specific': bool(specific_week),
            'previous_week': previous_week,
            'next_week': next_week,
            'planner_url': reverse('admin:appointments_weeklyschedule_planner'),
        }
        return render(request, 'admin/appointments/weekly_schedule/planner.html', context)


@admin.register(ScheduleException)
class ScheduleExceptionAdmin(admin.ModelAdmin):
    list_display = ('date', 'kind', 'start_time', 'end_time', 'note')
    list_filter = ('kind',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('jalali_date', 'start_time', 'patient', 'patient_phone', 'source', 'status')
    list_filter = ('date', 'source', 'status')
    search_fields = ('patient__full_name', 'patient__phone')
    date_hierarchy = 'date'
    autocomplete_fields = ('patient',)
    change_list_template = 'admin/appointments/appointment/change_list.html'

    @admin.display(description='تاریخ', ordering='date')
    def jalali_date(self, obj):
        return jalali_date_string(obj.date)

    @admin.display(description='موبایل')
    def patient_phone(self, obj):
        return obj.patient.phone

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('schedule/', self.admin_site.admin_view(self.schedule_view), name='appointments_appointment_schedule'),
        ]
        return custom + urls

    def schedule_view(self, request):
        try:
            selected_date = date.fromisoformat(request.GET.get('date', ''))
        except (TypeError, ValueError):
            selected_date = date.today() + timedelta(days=1)

        appointments = {
            appointment.start_time: appointment
            for appointment in Appointment.objects.select_related('patient').filter(
                date=selected_date,
                status=Appointment.BOOKED,
            )
        }
        slots = []
        for start, end in working_windows(selected_date):
            for slot in _slots_between(start, end):
                appointment = appointments.get(slot)
                slots.append({
                    'time': slot.strftime('%H:%M'),
                    'appointment': appointment,
                })

        context = {
            **self.admin_site.each_context(request),
            'title': 'تقویم نوبت‌ها',
            'opts': self.model._meta,
            'selected_date': selected_date,
            'jalali_selected_date': jalali_date_string(selected_date),
            'slots': slots,
            'appointment_count': len(appointments),
            'tomorrow': date.today() + timedelta(days=1),
            'yesterday': date.today() - timedelta(days=1),
        }
        return render(request, 'admin/appointments/appointment/schedule.html', context)


@admin.register(SiteImage)
class SiteImageAdmin(admin.ModelAdmin):
    list_display = ('get_key_display', 'preview', 'updated_at')
    fields = ('key', 'image', 'preview', 'alt_text')
    readonly_fields = ('preview',)

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:90px;border-radius:4px">', obj.image.url)
        return 'هنوز آپلود نشده — تصویر جایگزین در سایت نمایش داده می‌شود.'


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('caption', 'order', 'is_published', 'preview', 'created_at')
    list_editable = ('order', 'is_published')
    fields = ('order', 'is_published', 'image', 'preview', 'caption')
    readonly_fields = ('preview',)

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:90px;max-width:140px;object-fit:cover;border-radius:4px">', obj.image.url)
        return '—'


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('get_key_display', 'title', 'is_published', 'updated_at')
    list_editable = ('is_published',)
    fields = ('key', 'eyebrow', 'title', 'body', 'button_text', 'button_url', 'is_published', 'updated_at')
    readonly_fields = ('updated_at',)
