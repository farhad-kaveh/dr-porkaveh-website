from django import forms
from django.utils import timezone
class OnlineBookingForm(forms.Form):
    full_name=forms.CharField(label='نام و نام خانوادگی',max_length=120)
    phone=forms.CharField(label='شماره موبایل',max_length=20)
    date=forms.DateField(label='تاریخ',input_formats=['%Y-%m-%d'])
    slot=forms.TimeField(label='ساعت',input_formats=['%H:%M'])
    def clean_date(self):
        target = self.cleaned_data['date']
        if target < timezone.localdate():
            raise forms.ValidationError('تاریخ مراجعه نمی‌تواند در گذشته باشد.')
        return target

    def clean_phone(self):
        phone=self.cleaned_data['phone'].strip().replace(' ','')
        if len(phone)==10 and phone.startswith('9'): phone='0'+phone
        if not phone.isdigit() or len(phone)!=11 or not phone.startswith('09'):
            raise forms.ValidationError('شماره موبایل را به شکل 09xxxxxxxxx وارد کنید.')
        return phone
