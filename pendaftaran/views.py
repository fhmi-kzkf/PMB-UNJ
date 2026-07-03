"""
Views untuk aplikasi pendaftaran.

Menangani landing page, formulir pendaftaran, upload dokumen,
cetak bukti pendaftaran, dan cek hasil seleksi.
Sesuai PRD FR-01 s.d. FR-05, FR-11 s.d. FR-16, FR-21 dan TRD Bagian 7.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import Pendaftar, Dokumen, Jurusan, JalurMasuk, JadwalPenting
from .forms import PendaftaranForm, DokumenUploadForm
from .services.scoring import generate_no_registrasi, hitung_skor
from .services.report import generate_bukti_pdf


def landing_page(request):
    """
    View untuk halaman utama (landing page).

    Menampilkan:
    - Info kampus, visi-misi (FR-01).
    - Daftar jalur masuk (FR-02).
    - Timeline/jadwal penting (FR-03).
    - Estimasi biaya (FR-04).
    - FAQ dan kontak (FR-05).

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Render halaman landing page.
    """
    jalur_masuk = JalurMasuk.objects.all()
    jadwal = JadwalPenting.objects.all()
    jurusan_list = Jurusan.objects.all()
    total_pendaftar = Pendaftar.objects.count()

    context = {
        'jalur_masuk': jalur_masuk,
        'jadwal': jadwal,
        'jurusan_list': jurusan_list,
        'total_pendaftar': total_pendaftar,
        'total_jurusan': jurusan_list.count(),
    }
    return render(request, 'landing/home.html', context)


@login_required
def form_pendaftaran(request):
    """
    View untuk formulir pendaftaran mahasiswa baru komprehensif.

    GET: Menampilkan formulir pendaftaran 5 tahap.
    POST: Memproses data biodata, akademik, prodi, ortu, dan upload dokumen sekaligus.

    Sesuai PRD FR-11 s.d. FR-15.
    """
    # Cek apakah user sudah punya pendaftaran
    if Pendaftar.objects.filter(user=request.user).exists():
        messages.info(request, 'Anda sudah memiliki pendaftaran aktif.')
        return redirect('pendaftaran:status')

    if request.method == 'POST':
        form = PendaftaranForm(request.POST, request.FILES)
        if form.is_valid():
            pendaftar = form.save(commit=False)
            pendaftar.user = request.user
            pendaftar.no_registrasi = generate_no_registrasi()

            # Hitung skor akhir (nilai_tes default 0 sebelum ujian oleh admin)
            nilai_akademik = pendaftar.nilai_akademik or 0
            pendaftar.nilai_tes = 0  # Nilai tes belum diisi (diisi oleh admin setelah ujian)
            pendaftar.skor_akhir = hitung_skor(nilai_akademik, pendaftar.nilai_tes)

            pendaftar.save()

            # Simpan berkas-berkas dokumen (Tahap 5)
            dokumen_fields = {
                'pas_foto': 'file_pasfoto',
                'ktp': 'file_ktp',
                'kk': 'file_kk',
                'ijazah': 'file_ijazah',
                'sertifikat': 'file_sertifikat',
            }

            for jenis, field in dokumen_fields.items():
                file_obj = form.cleaned_data.get(field)
                if file_obj:
                    Dokumen.objects.create(
                        pendaftar=pendaftar,
                        jenis_dokumen=jenis,
                        file=file_obj,
                        status_verifikasi='belum_diverifikasi'
                    )

            messages.success(
                request,
                f'Pendaftaran berhasil disubmit! Nomor registrasi Anda: {pendaftar.no_registrasi}'
            )
            return redirect('pendaftaran:bukti')
    else:
        # Pre-fill data yang ada
        initial = {}
        if hasattr(request.user, 'profile'):
            initial['nama_lengkap'] = request.user.get_full_name() or ''
            initial['email'] = request.user.email or ''
        form = PendaftaranForm(initial=initial)

    return render(request, 'pendaftaran/form.html', {'form': form})


@login_required
def upload_dokumen(request):
    """
    View untuk mengunggah dokumen pendaftar.

    GET: Menampilkan form upload dan daftar dokumen yang sudah diupload.
    POST: Memproses file upload dengan validasi tipe dan ukuran.

    Sesuai PRD FR-14.

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Render halaman upload atau redirect.
    """
    pendaftar = get_object_or_404(Pendaftar, user=request.user)
    dokumen_list = pendaftar.dokumen.all()

    if request.method == 'POST':
        form = DokumenUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dokumen = form.save(commit=False)
            dokumen.pendaftar = pendaftar
            dokumen.save()
            messages.success(request, 'Dokumen berhasil diunggah!')
            return redirect('pendaftaran:upload_dokumen')
    else:
        form = DokumenUploadForm()

    context = {
        'form': form,
        'pendaftar': pendaftar,
        'dokumen_list': dokumen_list,
    }
    return render(request, 'pendaftaran/upload.html', context)


@login_required
def bukti_pendaftaran(request):
    """
    View untuk menampilkan dan mencetak bukti pendaftaran.

    Menampilkan halaman bukti pendaftaran dengan opsi download PDF.
    Sesuai PRD FR-16.

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Render halaman bukti atau PDF.
    """
    pendaftar = get_object_or_404(Pendaftar, user=request.user)

    if request.GET.get('format') == 'pdf':
        return generate_bukti_pdf(pendaftar)

    dokumen_list = pendaftar.dokumen.all()
    context = {
        'pendaftar': pendaftar,
        'dokumen_list': dokumen_list,
    }
    return render(request, 'pendaftaran/bukti.html', context)


@login_required
def status_pendaftaran(request):
    """
    View untuk melihat status pendaftaran pengguna.

    Menampilkan status seleksi, status pembayaran, dan data pendaftaran.

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Render halaman status atau redirect ke form.
    """
    try:
        pendaftar = Pendaftar.objects.select_related(
            'jurusan_pilihan1', 'jurusan_pilihan2', 'jalur_masuk'
        ).get(user=request.user)
        dokumen_list = pendaftar.dokumen.all()
    except Pendaftar.DoesNotExist:
        messages.info(request, 'Anda belum melakukan pendaftaran.')
        return redirect('pendaftaran:form')

    context = {
        'pendaftar': pendaftar,
        'dokumen_list': dokumen_list,
    }
    return render(request, 'pendaftaran/status.html', context)


def hasil_seleksi(request):
    """
    View publik untuk cek hasil seleksi berdasarkan nomor registrasi.

    GET: Menampilkan form pencarian.
    POST/GET dengan param: Menampilkan hasil seleksi.
    Sesuai PRD FR-21.

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Render halaman hasil seleksi.
    """
    pendaftar = None
    searched = False
    no_reg = request.GET.get('no_registrasi', '').strip()

    if no_reg:
        searched = True
        try:
            pendaftar = Pendaftar.objects.select_related(
                'jurusan_pilihan1', 'jurusan_pilihan2'
            ).get(no_registrasi=no_reg)
        except Pendaftar.DoesNotExist:
            messages.error(request, 'Nomor registrasi tidak ditemukan.')

    context = {
        'pendaftar': pendaftar,
        'searched': searched,
        'no_registrasi': no_reg,
    }
    return render(request, 'pendaftaran/hasil.html', context)
