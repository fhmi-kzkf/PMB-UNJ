"""
URL configuration untuk aplikasi dashboard.
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('pendaftar/', views.pendaftar_list, name='pendaftar_list'),
    path('pendaftar/<int:pk>/', views.detail_pendaftar, name='detail_pendaftar'),
    path('verifikasi/<int:dok_id>/', views.verifikasi_dokumen, name='verifikasi_dokumen'),
    path('jalankan-seleksi/', views.run_seleksi, name='run_seleksi'),
    path('status-bayar/<int:pk>/', views.update_status_bayar, name='update_status_bayar'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('kuota/', views.kelola_kuota, name='kelola_kuota'),
    path('acc/<int:pk>/', views.acc_pendaftar, name='acc_pendaftar'),
]
