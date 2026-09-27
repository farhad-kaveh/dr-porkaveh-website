from django.core.exceptions import ValidationError
from django.db import models

class Patient(models.Model):
    full_name=models.CharField('نام و نام خانوادگی',max_length=120)
    phone=models.CharField('شماره موبایل',max_length=20,db_index=True)
    created_at=models.DateTimeField('زمان ایجاد',auto_now_add=True)
    updated_at=models.DateTimeField('آخرین ویرایش',auto_now=True)
    class Meta:
        ordering=['-created_at']; verbose_name='بیمار'; verbose_name_plural='بیماران'
    def __str__(self): return f'{self.full_name} — {self.phone}'

class ScheduleWeek(models.Model):
    week_start=models.DateField('شروع هفته (شنبه)',unique=True)
    is_active=models.BooleanField('فعال',default=True)
    note=models.CharField('توضیح',max_length=250,blank=True)
    class Meta:
        ordering=['-week_start']; verbose_name='برنامه اختصاصی هفته'; verbose_name_plural='برنامه‌های اختصاصی هفته'
    def clean(self):
        # A clinic week always starts on Saturday.
        if self.week_start.weekday() != 5:
            raise ValidationError('شروع هفته باید شنبه باشد.')
    def __str__(self):
        return f'هفته شروع {self.week_start}'


class WeeklySchedule(models.Model):
    DAYS=[(0,'شنبه'),(1,'یکشنبه'),(2,'دوشنبه'),(3,'سه‌شنبه'),(4,'چهارشنبه'),(5,'پنجشنبه'),(6,'جمعه')]
    schedule_week=models.ForeignKey(ScheduleWeek,on_delete=models.CASCADE,related_name='days',verbose_name='هفته اختصاصی',null=True,blank=True)
    weekday=models.PositiveSmallIntegerField('روز هفته',choices=DAYS)
    start_time=models.TimeField('شروع'); end_time=models.TimeField('پایان')
    is_active=models.BooleanField('فعال',default=True)
    class Meta:
        ordering=['weekday','start_time']; verbose_name='برنامه هفتگی'; verbose_name_plural='برنامه هفتگی'
    def clean(self):
        if self.end_time<=self.start_time: raise ValidationError('زمان پایان باید بعد از شروع باشد.')
    def __str__(self): return f'{self.get_weekday_display()} | {self.start_time:%H:%M} تا {self.end_time:%H:%M}'

class ScheduleException(models.Model):
    CLOSED='closed'; CUSTOM='custom'
    KIND_CHOICES=[(CLOSED,'تعطیل'),(CUSTOM,'ساعت کاری خاص')]
    date=models.DateField('تاریخ',unique=True)
    kind=models.CharField('نوع',max_length=10,choices=KIND_CHOICES,default=CLOSED)
    start_time=models.TimeField('شروع',null=True,blank=True)
    end_time=models.TimeField('پایان',null=True,blank=True)
    note=models.CharField('توضیح',max_length=250,blank=True)
    class Meta:
        ordering=['date']; verbose_name='استثنای برنامه'; verbose_name_plural='استثناهای برنامه'
    def clean(self):
        if self.kind==self.CUSTOM:
            if not self.start_time or not self.end_time: raise ValidationError('برای ساعت خاص، شروع و پایان الزامی است.')
            if self.end_time<=self.start_time: raise ValidationError('پایان باید بعد از شروع باشد.')
    def __str__(self): return f'{self.date} — {self.get_kind_display()}'

class Appointment(models.Model):
    BOOKED='booked'; CANCELLED='cancelled'; COMPLETED='completed'; NO_SHOW='no_show'
    STATUS_CHOICES=[(BOOKED,'رزرو شده'),(CANCELLED,'لغو شده'),(COMPLETED,'انجام شده'),(NO_SHOW,'عدم مراجعه')]
    ONLINE='online'; RECEPTION='reception'
    SOURCE_CHOICES=[(ONLINE,'رزرو آنلاین'),(RECEPTION,'ثبت توسط منشی')]
    patient=models.ForeignKey(Patient,on_delete=models.PROTECT,related_name='appointments',verbose_name='بیمار')
    date=models.DateField('تاریخ',db_index=True)
    start_time=models.TimeField('شروع'); end_time=models.TimeField('پایان')
    status=models.CharField('وضعیت',max_length=12,choices=STATUS_CHOICES,default=BOOKED)
    source=models.CharField('منبع',max_length=10,choices=SOURCE_CHOICES,default=ONLINE)
    created_at=models.DateTimeField('زمان ثبت',auto_now_add=True)
    updated_at=models.DateTimeField('آخرین ویرایش',auto_now=True)
    class Meta:
        ordering=['date','start_time']; verbose_name='نوبت'; verbose_name_plural='نوبت‌ها'
        constraints=[models.UniqueConstraint(fields=['date','start_time'],condition=models.Q(status='booked'),name='unique_active_appointment_slot')]
    def clean(self):
        if self.end_time<=self.start_time: raise ValidationError('پایان باید بعد از شروع باشد.')
    def __str__(self): return f'{self.date} | {self.start_time:%H:%M} | {self.patient.full_name}'


class SiteImage(models.Model):
    """Single named image slots (hero, doctor, problem cards) the clinic
    owner can replace from the admin panel without any developer help.
    The homepage falls back to a placeholder graphic whenever a slot has
    no image uploaded yet."""
    HERO='hero'; DOCTOR='doctor'; PROBLEM_GUM='problem_gum'; PROBLEM_IMPLANT='problem_implant'
    KEY_CHOICES=[
        (HERO,'تصویر هیرو (پس‌زمینه صفحه اول)'),
        (DOCTOR,'عکس دکتر'),
        (PROBLEM_GUM,'تصویر کارت «بیماری لثه»'),
        (PROBLEM_IMPLANT,'تصویر کارت «بی‌دندانی»'),
    ]
    key=models.CharField('جایگاه تصویر',max_length=20,choices=KEY_CHOICES,unique=True)
    image=models.ImageField('تصویر',upload_to='site/',blank=True,null=True)
    alt_text=models.CharField('متن جایگزین (alt)',max_length=200,blank=True)
    updated_at=models.DateTimeField('آخرین ویرایش',auto_now=True)
    class Meta:
        ordering=['key']; verbose_name='تصویر ثابت سایت'; verbose_name_plural='تصاویر ثابت سایت'
    def __str__(self): return self.get_key_display()


class CaseStudy(models.Model):
    """A single-image portfolio item shown on the homepage.

    Portfolio images can be managed from Django admin or placed directly in
    static/appointments/img/cases/ using the local-file convention.
    """
    order=models.PositiveIntegerField('ترتیب نمایش',default=0)
    image=models.ImageField('عکس نمونه‌کار',upload_to='cases/')
    caption=models.CharField('کپشن (اختیاری)',max_length=200,blank=True)
    is_published=models.BooleanField('نمایش در سایت',default=True)
    created_at=models.DateTimeField('زمان ثبت',auto_now_add=True)
    class Meta:
        ordering=['order','id']; verbose_name='نمونه‌کار'; verbose_name_plural='نمونه‌کارها'
    def __str__(self): return self.caption or f'نمونه‌کار #{self.pk}'


class SiteContent(models.Model):
    """Editable public-facing content managed from the admin dashboard."""
    ABOUT='about'; EDUCATION='education'
    KEY_CHOICES=[
        (ABOUT,'درباره ما / معرفی دکتر'),
        (EDUCATION,'آموزش'),
    ]
    key=models.CharField('بخش',max_length=20,choices=KEY_CHOICES,unique=True)
    eyebrow=models.CharField('عنوان کوچک',max_length=120,blank=True)
    title=models.CharField('عنوان اصلی',max_length=250)
    body=models.TextField('متن')
    button_text=models.CharField('متن دکمه',max_length=120,blank=True)
    button_url=models.CharField('لینک دکمه',max_length=250,blank=True)
    is_published=models.BooleanField('نمایش در سایت',default=True)
    updated_at=models.DateTimeField('آخرین ویرایش',auto_now=True)
    class Meta:
        ordering=['key']; verbose_name='محتوای سایت'; verbose_name_plural='محتوای سایت'
    def __str__(self): return self.get_key_display()
