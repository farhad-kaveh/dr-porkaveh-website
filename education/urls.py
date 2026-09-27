from django.urls import path
from . import views
urlpatterns=[
    path('',views.index,name='education'),
    path('<str:slug>/',views.detail,name='education_detail'),
]
