from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("appointments.urls")),
    path("education/", include("education.urls")),
]

if settings.DEBUG:
    # Development only. In production, Liara's web server serves /media/.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
