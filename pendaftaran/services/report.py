"""
Modul report — fungsi untuk ekspor data dan generasi dokumen PDF.

Sesuai TRD Bagian 3 (Tech Stack: csv module, xhtml2pdf) dan PRD FR-16, FR-26.
"""

import csv
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template


def export_pendaftar_csv(queryset):
    """
    Mengekspor data pendaftar ke format CSV.

    Parameters:
        queryset (QuerySet): QuerySet dari model Pendaftar.

    Returns:
        HttpResponse: Response dengan konten CSV yang siap di-download.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data_pendaftar_pmb.csv"'
    response.write('\ufeff')  # BOM untuk Excel compatibility

    writer = csv.writer(response)
    writer.writerow([
        'No. Registrasi', 'Nama Lengkap', 'NIK', 'NISN',
        'Tempat Lahir', 'Tanggal Lahir', 'Alamat', 'No. HP',
        'Asal Sekolah', 'Jurusan Pilihan 1', 'Jurusan Pilihan 2',
        'Jalur Masuk', 'Nilai Akademik', 'Nilai Tes',
        'Skor Akhir', 'Status Seleksi', 'Status Bayar', 'Tanggal Daftar'
    ])

    for p in queryset.select_related('jurusan_pilihan1', 'jurusan_pilihan2', 'jalur_masuk'):
        writer.writerow([
            p.no_registrasi,
            p.nama_lengkap,
            p.nik,
            p.nisn,
            p.tempat_lahir,
            p.tanggal_lahir,
            p.alamat,
            p.no_hp,
            p.asal_sekolah,
            p.jurusan_pilihan1.nama_jurusan if p.jurusan_pilihan1 else '',
            p.jurusan_pilihan2.nama_jurusan if p.jurusan_pilihan2 else '',
            p.jalur_masuk.nama_jalur if p.jalur_masuk else '',
            p.nilai_akademik,
            p.nilai_tes,
            p.skor_akhir,
            p.get_status_seleksi_display(),
            p.get_status_bayar_display(),
            p.created_at.strftime('%Y-%m-%d %H:%M'),
        ])

    return response


def generate_bukti_pdf(pendaftar):
    """
    Menghasilkan Kartu Bukti Pendaftaran dalam format PDF.

    Menggunakan xhtml2pdf untuk mengkonversi template HTML ke PDF.

    Parameters:
        pendaftar (Pendaftar): Instance model Pendaftar.

    Returns:
        HttpResponse: Response dengan konten PDF yang siap di-download/tampilkan.
    """
    from xhtml2pdf import pisa

    template = get_template('pendaftaran/bukti_pdf.html')
    context = {
        'pendaftar': pendaftar,
        'dokumen_list': pendaftar.dokumen.all(),
    }
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="bukti_pendaftaran_{pendaftar.no_registrasi}.pdf"'
    )

    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Gagal membuat PDF', status=500)

    return response
