from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('booking/', views.booking, name='booking'),
    path('api/slots/', views.slots_api, name='slots_api'),
    path(
        'robots.txt',
        TemplateView.as_view(template_name='appointments/robots.txt', content_type='text/plain'),
        name='robots_txt',
    ),
    path('sitemap.xml', views.sitemap_view, name='sitemap_xml'),
]
