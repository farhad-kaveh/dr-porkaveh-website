from pathlib import Path

from django.templatetags.static import static


CASES_DIR = Path(__file__).resolve().parent / 'static' / 'appointments' / 'img' / 'cases'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

CATEGORY_ORDER = [
    ('ایمپلنت', 'implant'),
    ('جراحی لثه', 'gum-surgery'),
    ('پیوند لثه', 'gum-graft'),
    ('جراحی افزایش طول تاج', 'crown-lengthening'),
    ('جراحی دندان نهفته', 'impacted-tooth'),
]

CAPTIONS = {
    'ایمپلنت': {
        'case_01.jpg': 'جبران فضای بی‌دندانی با ایمپلنت',
        'case_03.png': 'چهار واحد ایمپلنت در طرح درمان اوردنچر مندیبل',
        'case_04.png': 'سینوس لیفت در مسیر آماده‌سازی برای درمان ایمپلنت',
        'Maxillary full arch implantation with left side open sinus lift.png': 'ایمپلنت تمام فک بالا همراه با سینوس لیفت باز در سمت چپ',
        'image_2026-09-16_08-07-07.png': 'نمونه‌ای از درمان ایمپلنت در فک بالا و پایین',
        'photo_2026-09-01_11-18-18.jpg': 'بازسازی گسترده دندان‌های از دست رفته با ایمپلنت',
    },
    'جراحی لثه': {
        'gum-flap-before-after.jpg': 'جراحی فلپ لثه؛ مقایسه قبل و بعد از درمان',
    },
    'پیوند لثه': {
        'Free gingival graft.png': 'پیوند لثه آزاد',
        'image_2026-09-16_08-12-13.png': 'نمونه‌ای از جراحی و پیوند لثه',
    },
    'جراحی افزایش طول تاج': {
        'case_02.png': 'افزایش طول تاج کلینیکی در ناحیه زیبایی',
        'case_03.png': 'افزایش طول تاج کلینیکی در ناحیه زیبایی',
        'image_2026-09-16_08-17-03.png': 'نمونه‌ای از افزایش طول تاج در ناحیه زیبایی',
    },
    'جراحی دندان نهفته': {
        'photo_2026-09-16_08-36-27.jpg': 'ارزیابی رادیوگرافیک کیس دندان نهفته',
        'image_2026-09-16_08-37-47.png': 'تصویر پانورامیک کیس دندان نهفته',
    },
}


def get_local_cases():
    """Load the clinic's local portfolio, grouped by treatment category."""
    if not CASES_DIR.exists():
        return []

    groups = []
    for category, folder_name in CATEGORY_ORDER:
        folder = CASES_DIR / folder_name
        if not folder.exists():
            continue
        items = []
        for image in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
            if not image.is_file() or image.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            items.append({
                'image_url': static(f'appointments/img/cases/{folder_name}/{image.name}'),
                'caption': CAPTIONS.get(category, {}).get(image.name, 'نمونه‌ای از درمان انجام‌شده'),
                'category': category,
                'is_before_after': image.name == 'gum-flap-before-after.jpg',
            })
        if items:
            groups.append({'name': category, 'items': items})

    return groups
