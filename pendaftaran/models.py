"""
Models untuk aplikasi pendaftaran PMB.

Berisi model-model utama: Jurusan, JalurMasuk, Pendaftar, Dokumen, JadwalPenting.
Sesuai dengan Database Schema pada dokumen Database_Schema_dan_App_Flow_PMB.md.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    FileExtensionValidator,
)


class Jurusan(models.Model):
    """
    Model untuk program studi / jurusan yang tersedia.

    Attributes:
        nama_jurusan (str): Nama program studi.
        akreditasi (str): Status akreditasi (A, B, Unggul, dll).
        kuota (int): Jumlah kuota utama penerimaan.
        kuota_cadangan (int): Jumlah kuota cadangan.
    """

    nama_jurusan = models.CharField(max_length=100, verbose_name='Nama Jurusan')
    akreditasi = models.CharField(max_length=10, blank=True, verbose_name='Akreditasi')
    kuota = models.PositiveIntegerField(default=0, verbose_name='Kuota Utama')
    kuota_cadangan = models.PositiveIntegerField(default=0, verbose_name='Kuota Cadangan')
    deskripsi = models.TextField(blank=True, verbose_name='Deskripsi Singkat')
    materi_pembelajaran = models.TextField(blank=True, verbose_name='Materi Pembelajaran')
    prospek_karir = models.TextField(blank=True, verbose_name='Prospek Karir')

    class Meta:
        verbose_name = 'Jurusan'
        verbose_name_plural = 'Jurusan'
        ordering = ['nama_jurusan']

    def __str__(self):
        return f"{self.nama_jurusan} ({self.akreditasi})"


class JalurMasuk(models.Model):
    """
    Model untuk jalur masuk penerimaan mahasiswa baru.

    Attributes:
        nama_jalur (str): Nama jalur (Reguler, Prestasi, KIP-K, Kerjasama).
        deskripsi (str): Deskripsi detail jalur masuk.
        periode_mulai (date): Tanggal mulai pendaftaran jalur.
        periode_selesai (date): Tanggal akhir pendaftaran jalur.
    """

    nama_jalur = models.CharField(max_length=50, verbose_name='Nama Jalur')
    deskripsi = models.TextField(blank=True, verbose_name='Deskripsi')
    periode_mulai = models.DateField(null=True, blank=True, verbose_name='Periode Mulai')
    periode_selesai = models.DateField(null=True, blank=True, verbose_name='Periode Selesai')

    class Meta:
        verbose_name = 'Jalur Masuk'
        verbose_name_plural = 'Jalur Masuk'
        ordering = ['periode_mulai']

    def __str__(self):
        return self.nama_jalur


class Pendaftar(models.Model):
    """
    Model utama untuk data pendaftar mahasiswa baru.

    Attributes:
        user (User): Relasi one-to-one dengan akun login Django.
        no_registrasi (str): Nomor registrasi unik (digenerate otomatis).
        nik (str): Nomor Induk Kependudukan (16 digit).
        nisn (str): Nomor Induk Siswa Nasional (10 digit).
        nama_lengkap (str): Nama lengkap pendaftar.
        tempat_lahir (str): Tempat lahir.
        tanggal_lahir (date): Tanggal lahir.
        alamat (str): Alamat lengkap.
        no_hp (str): Nomor handphone.
        asal_sekolah (str): Nama sekolah asal.
        jurusan_pilihan1 (Jurusan): Pilihan program studi pertama (wajib).
        jurusan_pilihan2 (Jurusan): Pilihan program studi kedua (opsional).
        jalur_masuk (JalurMasuk): Jalur masuk yang dipilih.
        nilai_akademik (Decimal): Nilai rata-rata rapor (0-100).
        nilai_tes (Decimal): Nilai tes seleksi (0-100).
        skor_akhir (Decimal): Skor akhir hasil perhitungan.
        status_seleksi (str): Status seleksi (menunggu/lulus/cadangan/tidak_lulus).
        status_bayar (str): Status pembayaran (belum_lunas/lunas).
        created_at (datetime): Waktu pendaftaran.
    """

    JURUSAN_SEKOLAH_CHOICES = [
        ('IPA', 'IPA'),
        ('IPS', 'IPS'),
        ('Bahasa', 'Bahasa'),
        ('Kejuruan', 'Kejuruan / SMK'),
    ]

    JENIS_KELAS_CHOICES = [
        ('reguler', 'Kelas Reguler / Pagi'),
        ('karyawan', 'Kelas Karyawan / Malam'),
    ]

    PEKERJAAN_ORTU_CHOICES = [
        ('pns', 'PNS / BUMN'),
        ('swasta', 'Karyawan Swasta'),
        ('wiraswasta', 'Wiraswasta / Pengusaha'),
        ('tni_polri', 'TNI / POLRI'),
        ('buruh', 'Buruh / Pekerja Lepas'),
        ('tani_nelayan', 'Petani / Nelayan'),
        ('tidak_bekerja', 'Tidak Bekerja / Pensiunan'),
        ('lainnya', 'Lainnya'),
    ]

    PENGHASILAN_ORTU_CHOICES = [
        ('kurang_1jt', 'Kurang dari Rp 1.000.000'),
        ('1jt_3jt', 'Rp 1.000.000 - Rp 3.000.000'),
        ('3jt_5jt', 'Rp 3.000.000 - Rp 5.000.000'),
        ('5jt_10jt', 'Rp 5.000.000 - Rp 10.000.000'),
        ('lebih_10jt', 'Lebih dari Rp 10.000.000'),
    ]

    STATUS_SELEKSI_CHOICES = [
        ('menunggu', 'Menunggu'),
        ('lulus', 'Lulus'),
        ('cadangan', 'Cadangan'),
        ('tidak_lulus', 'Tidak Lulus'),
    ]

    STATUS_BAYAR_CHOICES = [
        ('belum_lunas', 'Belum Lunas'),
        ('lunas', 'Lunas'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='pendaftar',
        verbose_name='Akun User'
    )
    no_registrasi = models.CharField(
        max_length=20, unique=True, verbose_name='No. Registrasi'
    )
    nik = models.CharField(max_length=16, unique=True, verbose_name='NIK')
    nisn = models.CharField(max_length=10, unique=True, verbose_name='NISN')
    nama_lengkap = models.CharField(max_length=150, verbose_name='Nama Lengkap')
    email = models.EmailField(default='', verbose_name='Email Aktif')
    tempat_lahir = models.CharField(
        max_length=100, blank=True, verbose_name='Tempat Lahir'
    )
    tanggal_lahir = models.DateField(
        null=True, blank=True, verbose_name='Tanggal Lahir'
    )
    alamat = models.TextField(blank=True, verbose_name='Alamat')
    no_hp = models.CharField(max_length=15, blank=True, verbose_name='No. HP (WhatsApp)')
    
    # Data Pendidikan & Akademik
    asal_sekolah = models.CharField(
        max_length=150, blank=True, verbose_name='Asal Sekolah'
    )
    jurusan_sekolah = models.CharField(
        max_length=20, choices=JURUSAN_SEKOLAH_CHOICES, default='IPA', verbose_name='Jurusan Sekolah'
    )
    tahun_lulus = models.PositiveIntegerField(null=True, blank=True, verbose_name='Tahun Lulus')
    nilai_akademik = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Nilai Akademik (Rapor)'
    )
    nilai_tes = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Nilai Tes'
    )

    # Pilihan Program Studi
    jurusan_pilihan1 = models.ForeignKey(
        Jurusan, on_delete=models.PROTECT, related_name='pendaftar_pilihan1',
        verbose_name='Jurusan Pilihan 1'
    )
    jurusan_pilihan2 = models.ForeignKey(
        Jurusan, on_delete=models.PROTECT, related_name='pendaftar_pilihan2',
        null=True, blank=True, verbose_name='Jurusan Pilihan 2'
    )
    jalur_masuk = models.ForeignKey(
        JalurMasuk, on_delete=models.PROTECT, related_name='pendaftar',
        verbose_name='Jalur Masuk'
    )
    jenis_kelas = models.CharField(
        max_length=20, choices=JENIS_KELAS_CHOICES, default='reguler', verbose_name='Jenis Kelas'
    )

    # Data Orang Tua / Wali
    nama_ayah = models.CharField(max_length=150, blank=True, verbose_name='Nama Ayah')
    nama_ibu = models.CharField(max_length=150, blank=True, verbose_name='Nama Ibu')
    no_hp_ortu = models.CharField(max_length=15, blank=True, verbose_name='No. HP Utama Orang Tua / Wali')
    no_hp_ortu_cadangan = models.CharField(max_length=15, blank=True, verbose_name='No. HP Cadangan (Opsional)')
    pekerjaan_ortu = models.CharField(
        max_length=30, choices=PEKERJAAN_ORTU_CHOICES, blank=True, verbose_name='Pekerjaan Orang Tua / Wali'
    )
    penghasilan_ortu = models.CharField(
        max_length=30, choices=PENGHASILAN_ORTU_CHOICES, blank=True, verbose_name='Penghasilan Orang Tua / Wali'
    )

    skor_akhir = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name='Skor Akhir'
    )
    status_seleksi = models.CharField(
        max_length=20, choices=STATUS_SELEKSI_CHOICES, default='menunggu',
        verbose_name='Status Seleksi'
    )
    status_bayar = models.CharField(
        max_length=15, choices=STATUS_BAYAR_CHOICES, default='belum_lunas',
        verbose_name='Status Pembayaran'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Tanggal Daftar')

    class Meta:
        verbose_name = 'Pendaftar'
        verbose_name_plural = 'Pendaftar'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['nisn'], name='idx_pendaftar_nisn'),
            models.Index(fields=['jurusan_pilihan1'], name='idx_pendaftar_jurusan1'),
            models.Index(fields=['status_seleksi'], name='idx_pendaftar_status'),
        ]

    def __str__(self):
        return f"{self.nama_lengkap} ({self.no_registrasi})"


class Dokumen(models.Model):
    """
    Model untuk dokumen yang diunggah oleh pendaftar.

    Attributes:
        pendaftar (Pendaftar): Relasi many-to-one dengan Pendaftar.
        jenis_dokumen (str): Jenis dokumen (ktp, kk, pas_foto, ijazah).
        file (File): File dokumen yang diunggah.
        status_verifikasi (str): Status verifikasi dokumen.
        uploaded_at (datetime): Waktu pengunggahan.
    """

    JENIS_DOKUMEN_CHOICES = [
        ('ktp', 'KTP / Kartu Identitas'),
        ('kk', 'Kartu Keluarga'),
        ('pas_foto', 'Pas Foto'),
        ('ijazah', 'Ijazah / SKL'),
        ('sertifikat', 'Sertifikat Prestasi'),
    ]

    STATUS_VERIFIKASI_CHOICES = [
        ('belum_diverifikasi', 'Belum Diverifikasi'),
        ('terverifikasi', 'Terverifikasi'),
        ('ditolak', 'Ditolak'),
    ]

    pendaftar = models.ForeignKey(
        Pendaftar, on_delete=models.CASCADE, related_name='dokumen',
        verbose_name='Pendaftar'
    )
    jenis_dokumen = models.CharField(
        max_length=30, choices=JENIS_DOKUMEN_CHOICES, verbose_name='Jenis Dokumen'
    )
    file = models.FileField(
        upload_to='dokumen/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name='File Dokumen'
    )
    status_verifikasi = models.CharField(
        max_length=20, choices=STATUS_VERIFIKASI_CHOICES,
        default='belum_diverifikasi', verbose_name='Status Verifikasi'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Tanggal Upload')

    class Meta:
        verbose_name = 'Dokumen'
        verbose_name_plural = 'Dokumen'
        ordering = ['pendaftar', 'jenis_dokumen']

    def __str__(self):
        return f"{self.get_jenis_dokumen_display()} - {self.pendaftar.nama_lengkap}"


class JadwalPenting(models.Model):
    """
    Model untuk jadwal/timeline penting PMB.

    Attributes:
        nama_kegiatan (str): Nama kegiatan.
        tanggal_mulai (date): Tanggal mulai kegiatan.
        tanggal_selesai (date): Tanggal selesai kegiatan.
    """

    nama_kegiatan = models.CharField(max_length=150, verbose_name='Nama Kegiatan')
    tanggal_mulai = models.DateField(null=True, blank=True, verbose_name='Tanggal Mulai')
    tanggal_selesai = models.DateField(null=True, blank=True, verbose_name='Tanggal Selesai')

    class Meta:
        verbose_name = 'Jadwal Penting'
        verbose_name_plural = 'Jadwal Penting'
        ordering = ['tanggal_mulai']

    def __str__(self):
        return self.nama_kegiatan
