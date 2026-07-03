"""
Views untuk aplikasi dashboard admin.

Menangani rekap pendaftar, verifikasi dokumen, seleksi, kuota, dan export.
Sesuai PRD FR-22 s.d. FR-27 dan TRD Bagian 7.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.views.decorators.http import require_POST

from pendaftaran.models import Pendaftar, Dokumen, Jurusan, JalurMasuk
from pendaftaran.services.scoring import jalankan_seleksi, jalankan_seleksi_semua
from pendaftaran.services.report import export_pendaftar_csv
from .decorators import admin_required


@admin_required
def dashboard_home(request):
    """
    View untuk halaman utama dashboard admin.

    Menampilkan statistik rekapitulasi:
    - Total pendaftar.
    - Jumlah per status seleksi.
    - Jumlah per jurusan (dengan annotate untuk menghindari N+1 query).
    - Dokumen yang belum diverifikasi.

    Sesuai PRD FR-22 dan TRD Bagian 9.4 (optimasi N+1 query).

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Render halaman dashboard home.
    """
    total_pendaftar = Pendaftar.objects.count()
    stats_seleksi = {
        'menunggu': Pendaftar.objects.filter(status_seleksi='menunggu').count(),
        'lulus': Pendaftar.objects.filter(status_seleksi='lulus').count(),
        'cadangan': Pendaftar.objects.filter(status_seleksi='cadangan').count(),
        'tidak_lulus': Pendaftar.objects.filter(status_seleksi='tidak_lulus').count(),
    }

    # Optimasi: gunakan annotate untuk menghindari N+1 query (TRD 9.4)
    jurusan_stats = Jurusan.objects.annotate(
        jumlah_pendaftar=Count('pendaftar_pilihan1')
    ).order_by('-jumlah_pendaftar')

    dokumen_pending = Dokumen.objects.filter(
        status_verifikasi='belum_diverifikasi'
    ).count()

    stats_bayar = {
        'lunas': Pendaftar.objects.filter(status_bayar='lunas').count(),
        'belum_lunas': Pendaftar.objects.filter(status_bayar='belum_lunas').count(),
    }

    context = {
        'total_pendaftar': total_pendaftar,
        'stats_seleksi': stats_seleksi,
        'jurusan_stats': jurusan_stats,
        'dokumen_pending': dokumen_pending,
        'stats_bayar': stats_bayar,
    }
    return render(request, 'dashboard/home.html', context)


@admin_required
def pendaftar_list(request):
    """
    View untuk menampilkan daftar pendaftar dengan filter.

    Filter yang tersedia (FR-22):
    - Per program studi (jurusan).
    - Per status seleksi.
    - Per jalur masuk.
    - Pencarian nama/NISN/no_registrasi.

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Render halaman daftar pendaftar.
    """
    queryset = Pendaftar.objects.select_related(
        'jurusan_pilihan1', 'jurusan_pilihan2', 'jalur_masuk'
    ).annotate(jumlah_dokumen=Count('dokumen'))

    # Filter
    jurusan_id = request.GET.get('jurusan', '')
    status = request.GET.get('status', '')
    jalur_id = request.GET.get('jalur', '')
    search = request.GET.get('q', '').strip()

    if jurusan_id:
        queryset = queryset.filter(jurusan_pilihan1_id=jurusan_id)
    if status:
        queryset = queryset.filter(status_seleksi=status)
    if jalur_id:
        queryset = queryset.filter(jalur_masuk_id=jalur_id)
    if search:
        queryset = queryset.filter(
            Q(nama_lengkap__icontains=search) |
            Q(nisn__icontains=search) |
            Q(no_registrasi__icontains=search)
        )

    context = {
        'pendaftar_list': queryset,
        'jurusan_list': Jurusan.objects.all(),
        'jalur_list': JalurMasuk.objects.all(),
        'filter_jurusan': jurusan_id,
        'filter_status': status,
        'filter_jalur': jalur_id,
        'filter_search': search,
    }
    return render(request, 'dashboard/pendaftar_list.html', context)


@admin_required
def detail_pendaftar(request, pk):
    """
    View untuk detail pendaftar dan verifikasi dokumen.

    Menampilkan semua data pendaftar beserta dokumen yang diunggah.
    Admin dapat memverifikasi atau menolak dokumen (FR-23).

    Parameters:
        request: HttpRequest object.
        pk (int): Primary key pendaftar.

    Returns:
        HttpResponse: Render halaman detail pendaftar.
    """
    pendaftar = get_object_or_404(
        Pendaftar.objects.select_related(
            'jurusan_pilihan1', 'jurusan_pilihan2', 'jalur_masuk', 'user'
        ),
        pk=pk
    )
    dokumen_list = pendaftar.dokumen.all()
    
    # Cek apakah semua dokumen terverifikasi
    semua_dokumen_valid = dokumen_list.exists() and all(d.status_verifikasi == 'terverifikasi' for d in dokumen_list)

    context = {
        'pendaftar': pendaftar,
        'dokumen_list': dokumen_list,
        'semua_dokumen_valid': semua_dokumen_valid,
    }
    return render(request, 'dashboard/detail_pendaftar.html', context)

@admin_required
@require_POST
def acc_pendaftar(request, pk):
    """
    View untuk ACC (Luluskan) pendaftar secara manual jika semua dokumen valid.
    """
    pendaftar = get_object_or_404(Pendaftar, pk=pk)
    
    dokumen_list = pendaftar.dokumen.all()
    semua_valid = dokumen_list.exists() and all(d.status_verifikasi == 'terverifikasi' for d in dokumen_list)
    
    if semua_valid:
        pendaftar.status_seleksi = 'lulus'
        pendaftar.save(update_fields=['status_seleksi'])
        messages.success(request, f'Pendaftar {pendaftar.nama_lengkap} berhasil di-ACC (Lulus).')
    else:
        messages.error(request, 'Gagal ACC: Semua dokumen harus terverifikasi terlebih dahulu.')
        
    return redirect('dashboard:detail_pendaftar', pk=pk)


@admin_required
@require_POST
def verifikasi_dokumen(request, dok_id):
    """
    View untuk memverifikasi dokumen pendaftar (FR-23).

    POST parameters:
    - status: 'terverifikasi' atau 'ditolak'.

    Parameters:
        request: HttpRequest object.
        dok_id (int): ID dokumen.

    Returns:
        HttpResponse: Redirect ke detail pendaftar.
    """
    dokumen = get_object_or_404(Dokumen, pk=dok_id)
    status = request.POST.get('status', '')

    if status in ('terverifikasi', 'ditolak'):
        dokumen.status_verifikasi = status
        dokumen.save(update_fields=['status_verifikasi'])
        status_display = 'diverifikasi' if status == 'terverifikasi' else 'ditolak'
        messages.success(
            request,
            f'Dokumen {dokumen.get_jenis_dokumen_display()} telah {status_display}.'
        )
    else:
        messages.error(request, 'Status verifikasi tidak valid.')

    return redirect('dashboard:detail_pendaftar', pk=dokumen.pendaftar.pk)


@admin_required
@require_POST
def run_seleksi(request):
    """
    View untuk menjalankan proses seleksi/ranking (FR-27).

    Dapat menjalankan seleksi per jurusan atau semua jurusan sekaligus.

    POST parameters:
    - jurusan_id (optional): ID jurusan spesifik, kosong = semua jurusan.

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Redirect ke dashboard dengan ringkasan hasil.
    """
    jurusan_id = request.POST.get('jurusan_id', '')

    if jurusan_id:
        hasil = jalankan_seleksi(int(jurusan_id))
        messages.success(
            request,
            f'Seleksi {hasil["jurusan"]} selesai: '
            f'{hasil["lulus"]} lulus, {hasil["cadangan"]} cadangan, '
            f'{hasil["tidak_lulus"]} tidak lulus.'
        )
    else:
        hasil_semua = jalankan_seleksi_semua()
        total_lulus = sum(h['lulus'] for h in hasil_semua)
        total = sum(h['total_pendaftar'] for h in hasil_semua)
        messages.success(
            request,
            f'Seleksi selesai untuk semua jurusan. '
            f'Total {total} pendaftar diproses, {total_lulus} lulus.'
        )

    return redirect('dashboard:home')


@admin_required
@require_POST
def update_status_bayar(request, pk):
    """
    View untuk mengubah status pembayaran pendaftar (FR-25).

    POST parameters:
    - status: 'lunas' atau 'belum_lunas'.

    Parameters:
        request: HttpRequest object.
        pk (int): Primary key pendaftar.

    Returns:
        HttpResponse: Redirect ke daftar pendaftar.
    """
    pendaftar = get_object_or_404(Pendaftar, pk=pk)
    status = request.POST.get('status', '')

    if status in ('lunas', 'belum_lunas'):
        pendaftar.status_bayar = status
        pendaftar.save(update_fields=['status_bayar'])
        messages.success(
            request,
            f'Status pembayaran {pendaftar.nama_lengkap} diubah menjadi {pendaftar.get_status_bayar_display()}.'
        )
    else:
        messages.error(request, 'Status pembayaran tidak valid.')

    return redirect('dashboard:pendaftar_list')


@admin_required
def export_csv(request):
    """
    View untuk mengekspor data pendaftar ke CSV (FR-26).

    Menerapkan filter yang sama dengan daftar pendaftar.

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: CSV file response.
    """
    queryset = Pendaftar.objects.select_related(
        'jurusan_pilihan1', 'jurusan_pilihan2', 'jalur_masuk'
    )

    # Apply filters
    jurusan_id = request.GET.get('jurusan', '')
    status = request.GET.get('status', '')
    if jurusan_id:
        queryset = queryset.filter(jurusan_pilihan1_id=jurusan_id)
    if status:
        queryset = queryset.filter(status_seleksi=status)

    return export_pendaftar_csv(queryset)


@admin_required
def kelola_kuota(request):
    """
    View untuk mengelola kuota program studi (FR-24).

    GET: Menampilkan tabel kuota.
    POST: Update kuota dan kuota_cadangan per jurusan.

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Render halaman kelola kuota atau redirect.
    """
    if request.method == 'POST':
        jurusan_id = request.POST.get('jurusan_id')
        kuota = request.POST.get('kuota', 0)
        kuota_cadangan = request.POST.get('kuota_cadangan', 0)

        jurusan = get_object_or_404(Jurusan, pk=jurusan_id)
        jurusan.kuota = int(kuota)
        jurusan.kuota_cadangan = int(kuota_cadangan)
        jurusan.save(update_fields=['kuota', 'kuota_cadangan'])

        messages.success(request, f'Kuota {jurusan.nama_jurusan} berhasil diperbarui.')
        return redirect('dashboard:kelola_kuota')

    jurusan_list = Jurusan.objects.annotate(
        jumlah_pendaftar=Count('pendaftar_pilihan1')
    )

    context = {
        'jurusan_list': jurusan_list,
    }
    return render(request, 'dashboard/kuota.html', context)
