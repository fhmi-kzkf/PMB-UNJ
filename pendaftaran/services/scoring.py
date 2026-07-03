"""
Modul scoring — logika bisnis perhitungan skor dan ranking pendaftar.

Modul ini dipisahkan dari views.py agar:
1. Mudah di-unit test secara independen.
2. Logika bisnis tidak bercampur dengan logika presentasi.
3. Dapat di-reuse dari berbagai konteks (view, management command, API).

Sesuai TRD Bagian 6 (Spesifikasi Algoritma) dan PRD FR-17 s.d. FR-20.
"""

import uuid
from decimal import Decimal
from django.utils import timezone


# Konstanta bobot penilaian
BOBOT_AKADEMIK = Decimal('0.6')
BOBOT_TES = Decimal('0.4')


def hitung_skor(nilai_akademik, nilai_tes):
    """
    Menghitung skor akhir pendaftar berdasarkan bobot akademik dan tes.

    Formula: skor_akhir = (nilai_akademik × 0.6) + (nilai_tes × 0.4)

    Parameters:
        nilai_akademik (float|Decimal): Nilai rapor/akademik, skala 0-100.
        nilai_tes (float|Decimal): Nilai tes seleksi, skala 0-100.

    Returns:
        Decimal: Skor akhir gabungan, skala 0-100, dibulatkan 2 desimal.

    Raises:
        ValueError: Jika nilai di luar rentang 0-100.

    Examples:
        >>> hitung_skor(80, 90)
        Decimal('84.00')
        >>> hitung_skor(0, 0)
        Decimal('0.00')
    """
    nilai_akademik = Decimal(str(nilai_akademik))
    nilai_tes = Decimal(str(nilai_tes))

    if not (0 <= nilai_akademik <= 100):
        raise ValueError(f"nilai_akademik harus 0-100, diterima: {nilai_akademik}")
    if not (0 <= nilai_tes <= 100):
        raise ValueError(f"nilai_tes harus 0-100, diterima: {nilai_tes}")

    skor = (nilai_akademik * BOBOT_AKADEMIK) + (nilai_tes * BOBOT_TES)
    return skor.quantize(Decimal('0.01'))


def ranking_pendaftar(daftar_pendaftar, kuota, kuota_cadangan=0):
    """
    Mengurutkan pendaftar berdasarkan skor akhir dan menentukan status kelulusan.

    Algoritma:
    1. Sort descending berdasarkan skor_akhir.
    2. Tie-breaker: urutkan berdasarkan nilai_akademik tertinggi.
    3. Tetapkan status berdasarkan posisi ranking terhadap kuota.

    Kompleksitas waktu: O(n log n) — didominasi proses sorting.

    Parameters:
        daftar_pendaftar (list[dict]): List pendaftar dengan key
            'skor_akhir' dan 'nilai_akademik'.
        kuota (int): Jumlah kuota utama program studi.
        kuota_cadangan (int): Jumlah kuota cadangan (default: 0).

    Returns:
        list[dict]: Daftar pendaftar terurut dengan tambahan key 'status_seleksi'
            dan 'ranking'.
    """
    hasil = sorted(
        daftar_pendaftar,
        key=lambda x: (
            float(x.get('skor_akhir', 0)),
            float(x.get('nilai_akademik', 0))
        ),
        reverse=True
    )

    for i, p in enumerate(hasil):
        p['ranking'] = i + 1
        if i < kuota:
            p['status_seleksi'] = 'lulus'
        elif i < kuota + kuota_cadangan:
            p['status_seleksi'] = 'cadangan'
        else:
            p['status_seleksi'] = 'tidak_lulus'

    return hasil


def generate_no_registrasi():
    """
    Menghasilkan nomor registrasi unik untuk pendaftar baru.

    Format: PMB-{TAHUN}-{5_DIGIT_RANDOM}
    Contoh: PMB-2026-A3F8C

    Returns:
        str: Nomor registrasi unik (max 20 karakter).
    """
    tahun = timezone.now().year
    unique_part = uuid.uuid4().hex[:5].upper()
    return f"PMB-{tahun}-{unique_part}"


def jalankan_seleksi(jurusan_id):
    """
    Menjalankan proses seleksi lengkap untuk satu jurusan.

    Langkah:
    1. Ambil semua pendaftar yang memilih jurusan tersebut sebagai pilihan 1.
    2. Hitung skor akhir masing-masing pendaftar.
    3. Lakukan ranking dan tentukan status kelulusan.
    4. Update database dengan skor_akhir dan status_seleksi.

    Parameters:
        jurusan_id (int): ID jurusan yang akan diseleksi.

    Returns:
        dict: Ringkasan hasil seleksi berisi jumlah lulus, cadangan, tidak_lulus.
    """
    from pendaftaran.models import Pendaftar, Jurusan

    jurusan = Jurusan.objects.get(pk=jurusan_id)
    pendaftar_qs = Pendaftar.objects.filter(jurusan_pilihan1=jurusan)

    # Hitung skor akhir untuk setiap pendaftar
    daftar = []
    for p in pendaftar_qs:
        if p.nilai_akademik is not None and p.nilai_tes is not None:
            skor = hitung_skor(p.nilai_akademik, p.nilai_tes)
            p.skor_akhir = skor
            p.save(update_fields=['skor_akhir'])
            daftar.append({
                'id': p.id,
                'nama': p.nama_lengkap,
                'skor_akhir': float(skor),
                'nilai_akademik': float(p.nilai_akademik),
            })

    # Ranking dan penentuan status
    hasil = ranking_pendaftar(daftar, jurusan.kuota, jurusan.kuota_cadangan)

    # Update status_seleksi ke database
    ringkasan = {'lulus': 0, 'cadangan': 0, 'tidak_lulus': 0}
    for h in hasil:
        Pendaftar.objects.filter(pk=h['id']).update(
            status_seleksi=h['status_seleksi']
        )
        ringkasan[h['status_seleksi']] += 1

    return {
        'jurusan': jurusan.nama_jurusan,
        'total_pendaftar': len(hasil),
        **ringkasan,
    }


def jalankan_seleksi_semua():
    """
    Menjalankan proses seleksi untuk semua jurusan.

    Returns:
        list[dict]: List ringkasan hasil seleksi per jurusan.
    """
    from pendaftaran.models import Jurusan

    hasil_semua = []
    for jurusan in Jurusan.objects.all():
        hasil = jalankan_seleksi(jurusan.id)
        hasil_semua.append(hasil)

    return hasil_semua
