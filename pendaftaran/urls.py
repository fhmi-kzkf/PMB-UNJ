"""
URL configuration untuk aplikasi pendaftaran.
"""

from django.urls import path
from . import views

app_name = 'pendaftaran'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('pendaftaran/form/', views.form_pendaftaran, name='form'),
    path('pendaftaran/upload/', views.upload_dokumen, name='upload_dokumen'),
    path('pendaftaran/bukti/', views.bukti_pendaftaran, name='bukti'),
    path('pendaftaran/status/', views.status_pendaftaran, name='status'),
    path('pendaftaran/hasil/', views.hasil_seleksi, name='hasil'),
]
