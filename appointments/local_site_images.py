from pathlib import Path
from django.templatetags.static import static

BASE_DIR = Path(__file__).resolve().parent / 'static' / 'appointments' / 'img'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def get_local_doctor_image():
    """Return the first image from img/doctor/ if one exists."""
    directory = BASE_DIR / 'doctor'
    if not directory.exists():
        return ''
    images = sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    return static(f'appointments/img/doctor/{images[0].name}') if images else ''
