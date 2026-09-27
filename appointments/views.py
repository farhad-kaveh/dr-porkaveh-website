from datetime import date
from django.utils import timezone
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from .forms import OnlineBookingForm
from .models import CaseStudy
from .local_cases import get_local_cases
from .services import available_slots, create_appointment
from .jalali import jalali_date_string
from education.models import Article


def home(request):
    """Public marketing homepage. Contains no patient data."""
    # Real cases can be added directly to static/appointments/img/cases/.
    # If that folder is empty, keep the existing Admin-based cases as a fallback.
    local_cases = get_local_cases()
    case_studies = local_cases or CaseStudy.objects.filter(is_published=True)
    return render(request, 'appointments/home.html', {
        'case_studies': case_studies,
        'local_case_studies': bool(local_cases),
    })


def booking(request):
    if request.method == 'POST':
        form = OnlineBookingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data['slot'] not in available_slots(data['date']):
                form.add_error('slot', 'این زمان دیگر آزاد نیست.')
            else:
                try:
                    appointment = create_appointment(
                        full_name=data['full_name'].strip(),
                        phone=data['phone'],
                        target_date=data['date'],
                        start_time=data['slot'],
                    )
                except IntegrityError:
                    form.add_error('slot', 'این زمان توسط بیمار دیگری رزرو شد. زمان دیگری انتخاب کنید.')
                else:
                    return render(request, 'appointments/success.html', {'appointment': appointment, 'jalali_date': jalali_date_string(appointment.date)})
    else:
        form = OnlineBookingForm()
    return render(request, 'appointments/booking.html', {'form': form, 'today': timezone.localdate().isoformat()})


def slots_api(request):
    try:
        target_date = date.fromisoformat(request.GET.get('date', ''))
    except ValueError:
        return JsonResponse({'slots': []}, status=400)
    return JsonResponse({
        'date': target_date.isoformat(),
        'slots': [x.strftime('%H:%M') for x in available_slots(target_date)],
    })


def sitemap_view(request):
    return render(request, 'appointments/sitemap.xml', {'education_articles': Article.objects.filter(is_published=True)})
