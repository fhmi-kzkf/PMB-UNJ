"""
Registrasi model pendaftaran ke Django Admin.
"""

from django.contrib import admin
from .models import Jurusan, JalurMasuk, Pendaftar, Dokumen, JadwalPenting


@admin.register(Jurusan)
class JurusanAdmin(admin.ModelAdmin):
    list_display = ('nama_jurusan', 'akreditasi', 'kuota', 'kuota_cadangan')
    search_fields = ('nama_jurusan',)


@admin.register(JalurMasuk)
class JalurMasukAdmin(admin.ModelAdmin):
    list_display = ('nama_jalur', 'periode_mulai', 'periode_selesai')
    search_fields = ('nama_jalur',)


class DokumenInline(admin.TabularInline):
    """Inline dokumen di halaman Pendaftar admin."""
    model = Dokumen
    extra = 0
    readonly_fields = ('uploaded_at',)


@admin.register(Pendaftar)
class PendaftarAdmin(admin.ModelAdmin):
    list_display = (
        'no_registrasi', 'nama_lengkap', 'nisn',
        'jurusan_pilihan1', 'jalur_masuk',
        'skor_akhir', 'status_seleksi', 'status_bayar', 'created_at'
    )
    list_filter = ('status_seleksi', 'status_bayar', 'jurusan_pilihan1', 'jalur_masuk')
    search_fields = ('nama_lengkap', 'nisn', 'nik', 'no_registrasi')
    readonly_fields = ('no_registrasi', 'skor_akhir', 'created_at')
    inlines = [DokumenInline]


@admin.register(Dokumen)
class DokumenAdmin(admin.ModelAdmin):
    list_display = ('pendaftar', 'jenis_dokumen', 'status_verifikasi', 'uploaded_at')
    list_filter = ('jenis_dokumen', 'status_verifikasi')
    search_fields = ('pendaftar__nama_lengkap',)


@admin.register(JadwalPenting)
class JadwalPentingAdmin(admin.ModelAdmin):
    list_display = ('nama_kegiatan', 'tanggal_mulai', 'tanggal_selesai')
    ordering = ('tanggal_mulai',)
