from .models import SiteImage, SiteContent
from .local_site_images import get_local_doctor_image


def site_images(request):
    """Makes {{ site_images.hero }} etc. available in every template.
    Value is the uploaded image's URL, or missing entirely if nothing
    has been uploaded yet for that slot (templates fall back to a
    static placeholder in that case)."""
    urls = {
        item.key: item.image.url
        for item in SiteImage.objects.exclude(image='').exclude(image__isnull=True)
    }
    content = {item.key: item for item in SiteContent.objects.filter(is_published=True)}
    doctor_local = get_local_doctor_image()
    if doctor_local:
        urls['doctor_local'] = doctor_local
    return {'site_images': urls, 'site_content': content}
