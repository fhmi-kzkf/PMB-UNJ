# Technical Requirement Document (TRD)
# Sistem Informasi Penerimaan Mahasiswa Baru (PMB)
### Universitas Nusantara Jaya (Studi Kasus Fiktif)

| | |
|---|---|
| **Versi Dokumen** | 1.0 |
| **Tanggal** | 3 Juli 2026 |
| **Disusun oleh** | Analis Program |
| **Dokumen Terkait** | PRD_Sistem_Informasi_PMB.md |
| **Status** | Final untuk Asesmen |

---

## 1. Tujuan Dokumen

Dokumen ini menjabarkan **spesifikasi teknis** implementasi Sistem Informasi PMB berdasarkan kebutuhan fungsional dan non-fungsional yang telah ditetapkan pada PRD. TRD ini menjadi acuan bagi proses coding, code review, testing, debugging, dan profiling yang akan didemonstrasikan pada sesi asesmen.

---

## 2. Arsitektur Sistem

### 2.1 Gaya Arsitektur
Aplikasi menggunakan pola **MVT (Model-View-Template)** bawaan Django, dengan penambahan **service layer** untuk memisahkan logika bisnis (algoritma) dari view — agar mudah di-unit test secara independen.

```
Client (Browser)
      │  HTTP Request
      ▼
┌─────────────────────────────────────┐
│              Django App              │
│                                       │
│  urls.py  →  views.py  →  services/  │
│                  │            │       │
│                  ▼            ▼       │
│              templates/    models.py  │
└─────────────────────────────────────┘
      │
      ▼
   SQLite / PostgreSQL (Database)
```

### 2.2 Pola Desain
- **MVT (Model-View-Template)** — arsitektur inti Django.
- **Service Layer Pattern** — logika bisnis (scoring, ranking) dipisah ke `services/scoring.py`, tidak ditulis langsung di `views.py`.
- **Repository-like access** — akses data terpusat melalui Django ORM (Manager/QuerySet), menghindari raw SQL kecuali untuk kebutuhan reporting kompleks.

---

## 3. Spesifikasi Teknologi (Tech Stack)

| Layer | Teknologi | Keterangan |
|-------|-----------|------------|
| Bahasa Pemrograman | Python 3.11+ | |
| Framework Web | Django 5.x | Termasuk Django Admin (bawaan) |
| Basis Data (Dev) | SQLite 3 | Untuk kemudahan development & demo |
| Basis Data (Opsional Prod) | PostgreSQL | Disebutkan sebagai rencana scaling |
| ORM | Django ORM | Parameterized query otomatis (anti SQL Injection) |
| Frontend | Django Template + Bootstrap 5 | Server-side rendering, responsif |
| Autentikasi | Django Auth (built-in) | Register, login, reset password, hashing PBKDF2 |
| Testing | Django TestCase / pytest-django | Unit test & integration test |
| Profiling | Django Debug Toolbar, cProfile | Analisis query time & jumlah query |
| Debugging | pdb / breakpoint(), Django Debug Toolbar | Debugging interaktif |
| Version Control | Git | Riwayat perubahan kode, mendukung code review |
| Dependency Management | pip + requirements.txt / virtualenv | Reproducibility environment |
| Export Laporan | Python `csv` module / `openpyxl` | Export data pendaftar |
| Cetak Dokumen | `xhtml2pdf` / `WeasyPrint` | Cetak Kartu Bukti Pendaftaran (PDF) |

---

## 4. Struktur Proyek (Project Structure)

```
pmb_system/
│
├── manage.py
├── requirements.txt
├── .env                          # konfigurasi rahasia (SECRET_KEY, DB, dll)
│
├── pmb_config/                   # root config project Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                     # app: autentikasi & user
│   ├── models.py                 # extend User (role)
│   ├── views.py                  # register, login, reset password
│   ├── forms.py
│   └── urls.py
│
├── pendaftaran/                  # app: modul inti PMB
│   ├── models.py                 # Pendaftar, Jurusan, JalurMasuk, Dokumen
│   ├── views.py                  # form pendaftaran, upload dokumen
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py                  # registrasi model ke Django Admin
│   └── services/
│       ├── scoring.py            # hitung_skor(), ranking_pendaftar()
│       └── report.py             # export_csv()
│
├── dashboard/                    # app: dashboard admin
│   ├── views.py                  # rekap data, verifikasi, kelola kuota
│   └── urls.py
│
├── templates/
│   ├── landing/
│   ├── accounts/
│   ├── pendaftaran/
│   └── dashboard/
│
├── static/                       # CSS, JS, gambar
│
├── tests/
│   ├── test_unit_scoring.py      # unit test algoritma
│   ├── test_unit_forms.py        # unit test validasi form
│   └── test_integration_flow.py  # integration test alur pendaftaran-seleksi
│
└── docs/
    ├── ERD.png
    ├── coding_guidelines.md
    └── api_docs.md (jika ada endpoint API)
```

---

## 5. Rancangan Basis Data (Database Design)

### 5.1 Skema Tabel (DDL)

```sql
-- Tabel Jurusan
CREATE TABLE jurusan (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_jurusan  VARCHAR(100) NOT NULL,
    akreditasi    VARCHAR(5),
    kuota         INTEGER NOT NULL DEFAULT 0,
    kuota_cadangan INTEGER NOT NULL DEFAULT 0
);

-- Tabel Jalur Masuk
CREATE TABLE jalur_masuk (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_jalur        VARCHAR(50) NOT NULL,
    deskripsi         TEXT,
    periode_mulai     DATE,
    periode_selesai   DATE
);

-- Tabel Pendaftar
CREATE TABLE pendaftar (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER UNIQUE NOT NULL,
    no_registrasi    VARCHAR(20) UNIQUE NOT NULL,
    nik              VARCHAR(16) UNIQUE NOT NULL,
    nisn             VARCHAR(10) UNIQUE NOT NULL,
    nama_lengkap     VARCHAR(150) NOT NULL,
    tempat_lahir     VARCHAR(100),
    tanggal_lahir    DATE,
    alamat           TEXT,
    no_hp            VARCHAR(15),
    jurusan_pilihan1 INTEGER NOT NULL,
    jurusan_pilihan2 INTEGER,
    jalur_masuk_id   INTEGER NOT NULL,
    nilai_akademik   DECIMAL(5,2),
    nilai_tes        DECIMAL(5,2),
    skor_akhir       DECIMAL(5,2),
    status_seleksi   VARCHAR(20) DEFAULT 'menunggu',  -- menunggu|lulus|cadangan|tidak_lulus
    status_bayar     VARCHAR(15) DEFAULT 'belum_lunas', -- lunas|belum_lunas
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    FOREIGN KEY (jurusan_pilihan1) REFERENCES jurusan(id),
    FOREIGN KEY (jurusan_pilihan2) REFERENCES jurusan(id),
    FOREIGN KEY (jalur_masuk_id) REFERENCES jalur_masuk(id)
);

-- Tabel Dokumen
CREATE TABLE dokumen (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    pendaftar_id       INTEGER NOT NULL,
    jenis_dokumen      VARCHAR(30) NOT NULL, -- ktp|kk|pas_foto|ijazah
    file_path          VARCHAR(255) NOT NULL,
    status_verifikasi  VARCHAR(20) DEFAULT 'belum_diverifikasi',
    uploaded_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pendaftar_id) REFERENCES pendaftar(id)
);

-- Index untuk performa query (NFR-01)
CREATE INDEX idx_pendaftar_nisn ON pendaftar(nisn);
CREATE INDEX idx_pendaftar_jurusan1 ON pendaftar(jurusan_pilihan1);
CREATE INDEX idx_pendaftar_status ON pendaftar(status_seleksi);
```

### 5.2 Contoh Query Kunci

```sql
-- Rekap jumlah pendaftar per jurusan (dipakai di dashboard admin)
SELECT j.nama_jurusan, COUNT(p.id) AS jumlah_pendaftar, j.kuota
FROM jurusan j
LEFT JOIN pendaftar p ON p.jurusan_pilihan1 = j.id
GROUP BY j.id
ORDER BY jumlah_pendaftar DESC;

-- Ranking pendaftar per jurusan (dasar algoritma seleksi)
SELECT nama_lengkap, nisn, skor_akhir, nilai_akademik
FROM pendaftar
WHERE jurusan_pilihan1 = ?
ORDER BY skor_akhir DESC, nilai_akademik DESC;

-- Cek jumlah dokumen yang belum diverifikasi (query untuk profiling)
SELECT p.nama_lengkap, COUNT(d.id) AS dokumen_pending
FROM pendaftar p
JOIN dokumen d ON d.pendaftar_id = p.id AND d.status_verifikasi = 'belum_diverifikasi'
GROUP BY p.id;
```

> Query di atas akan didemonstrasikan bersama hasil `EXPLAIN QUERY PLAN` saat sesi profiling untuk menunjukkan efektivitas index.

---

## 6. Spesifikasi Algoritma

### 6.1 Fungsi Perhitungan Skor

```python
def hitung_skor(nilai_akademik: float, nilai_tes: float) -> float:
    """
    Menghitung skor akhir pendaftar berdasarkan bobot akademik dan tes.

    Parameters:
        nilai_akademik (float): nilai rapor/akademik, skala 0-100
        nilai_tes (float): nilai tes seleksi, skala 0-100

    Returns:
        float: skor akhir gabungan, skala 0-100
    """
    BOBOT_AKADEMIK = 0.6
    BOBOT_TES = 0.4
    return round((nilai_akademik * BOBOT_AKADEMIK) + (nilai_tes * BOBOT_TES), 2)
```

### 6.2 Fungsi Ranking & Penentuan Status

```python
def ranking_pendaftar(daftar_pendaftar: list, kuota: int, kuota_cadangan: int = 0) -> list:
    """
    Mengurutkan pendaftar berdasarkan skor akhir dan menentukan status kelulusan.

    Kompleksitas waktu: O(n log n) — didominasi proses sorting.

    Parameters:
        daftar_pendaftar (list[dict]): list pendaftar dengan key 'skor_akhir', 'nilai_akademik'
        kuota (int): jumlah kuota utama program studi
        kuota_cadangan (int): jumlah kuota cadangan

    Returns:
        list[dict]: daftar pendaftar terurut dengan tambahan key 'status_seleksi'
    """
    hasil = sorted(
        daftar_pendaftar,
        key=lambda x: (x['skor_akhir'], x['nilai_akademik']),
        reverse=True
    )

    for i, p in enumerate(hasil):
        if i < kuota:
            p['status_seleksi'] = 'lulus'
        elif i < kuota + kuota_cadangan:
            p['status_seleksi'] = 'cadangan'
        else:
            p['status_seleksi'] = 'tidak_lulus'

    return hasil
```

---

## 7. Spesifikasi API / Endpoint Internal

| Method | Endpoint | Fungsi | Auth |
|--------|----------|--------|------|
| GET | `/` | Landing page | Publik |
| GET/POST | `/accounts/register/` | Registrasi akun | Publik |
| GET/POST | `/accounts/login/` | Login | Publik |
| POST | `/accounts/logout/` | Logout | Terautentikasi |
| GET/POST | `/pendaftaran/form/` | Isi formulir pendaftaran | Terautentikasi |
| POST | `/pendaftaran/upload/` | Upload dokumen | Terautentikasi |
| GET | `/pendaftaran/bukti/<no_registrasi>/` | Cetak bukti pendaftaran (PDF) | Terautentikasi |
| GET | `/pendaftaran/hasil/<no_registrasi>/` | Lihat hasil seleksi | Publik (dengan no. registrasi) |
| GET | `/dashboard/` | Dashboard rekap admin | Admin |
| GET | `/dashboard/pendaftar/` | List & filter pendaftar | Admin |
| POST | `/dashboard/verifikasi/<id>/` | Verifikasi dokumen pendaftar | Admin |
| POST | `/dashboard/jalankan-seleksi/` | Trigger proses ranking | Admin |
| GET | `/dashboard/export/csv/` | Export data pendaftar (CSV) | Admin |

---

## 8. Strategi Keamanan (Security Considerations)

| Risiko | Mitigasi |
|--------|----------|
| SQL Injection | Menggunakan Django ORM (parameterized query), hindari raw SQL string formatting |
| Cross-Site Request Forgery (CSRF) | Django CSRF token aktif di semua form |
| Password lemah/plaintext | Password hashing menggunakan PBKDF2 (default Django) |
| Unauthorized access ke dashboard admin | `@login_required` + `@user_passes_test(is_admin)` decorator |
| Upload file berbahaya | Validasi ekstensi file (pdf, jpg, png) dan ukuran maksimal (≤2MB) |
| Data pribadi (NIK/NISN) | Tidak ditampilkan penuh di halaman publik, hanya bisa dilihat admin |

---

## 9. Strategi Pengujian (Test Plan Teknis)

### 9.1 Unit Test

```python
# tests/test_unit_scoring.py
from django.test import TestCase
from pendaftaran.services.scoring import hitung_skor, ranking_pendaftar

class ScoringTestCase(TestCase):

    def test_hitung_skor_normal(self):
        hasil = hitung_skor(80, 90)
        self.assertEqual(hasil, 84.0)  # (80*0.6)+(90*0.4)

    def test_hitung_skor_nilai_nol(self):
        hasil = hitung_skor(0, 0)
        self.assertEqual(hasil, 0.0)

    def test_ranking_tie_breaker(self):
        data = [
            {'nama': 'A', 'skor_akhir': 80, 'nilai_akademik': 85},
            {'nama': 'B', 'skor_akhir': 80, 'nilai_akademik': 90},
        ]
        hasil = ranking_pendaftar(data, kuota=1)
        self.assertEqual(hasil[0]['nama'], 'B')  # menang tie-breaker
        self.assertEqual(hasil[0]['status_seleksi'], 'lulus')
        self.assertEqual(hasil[1]['status_seleksi'], 'tidak_lulus')
```

### 9.2 Integration Test

```python
# tests/test_integration_flow.py
from django.test import TestCase, Client
from django.contrib.auth.models import User

class PendaftaranFlowTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='calon1', password='test1234')

    def test_alur_pendaftaran_sampai_seleksi(self):
        # 1. Login
        self.client.login(username='calon1', password='test1234')

        # 2. Submit formulir pendaftaran
        response = self.client.post('/pendaftaran/form/', {
            'nama_lengkap': 'Budi Santoso',
            'nik': '3201010101010001',
            'nisn': '0012345678',
            'nilai_akademik': 85,
            'nilai_tes': 78,
            'jurusan_pilihan1': 1,
        })
        self.assertEqual(response.status_code, 302)  # redirect setelah sukses

        # 3. Cek data tersimpan di DB
        from pendaftaran.models import Pendaftar
        self.assertTrue(Pendaftar.objects.filter(nisn='0012345678').exists())

        # 4. Jalankan proses seleksi (trigger oleh admin secara terpisah)
        # 5. Cek hasil seleksi dapat diakses
        pendaftar = Pendaftar.objects.get(nisn='0012345678')
        response = self.client.get(f'/pendaftaran/hasil/{pendaftar.no_registrasi}/')
        self.assertEqual(response.status_code, 200)
```

### 9.3 Skenario Debugging (Terencana untuk Demo)

| Bug yang Disimulasikan | Gejala | Cara Penelusuran | Perbaikan |
|--------------------------|--------|-------------------|-----------|
| Nilai disimpan sebagai string dari form input | `hitung_skor()` menghasilkan `TypeError` atau concat string | `breakpoint()` di `views.py` sebelum pemanggilan `hitung_skor()`, cek tipe data | Tambahkan `float()` casting eksplisit + validasi form (`forms.DecimalField`) |

### 9.4 Skenario Profiling (Terencana untuk Demo)

| Area yang Diprofil | Tools | Temuan yang Ditunjukkan |
|----------------------|-------|--------------------------|
| Halaman dashboard rekap pendaftar | Django Debug Toolbar | Query N+1 saat menampilkan jumlah dokumen per pendaftar tanpa `select_related`/`prefetch_related` |
| Fungsi `ranking_pendaftar()` untuk 1000 data dummy | `cProfile` + `pstats` | Waktu eksekusi sorting, dibandingkan sebelum/sesudah optimasi |

**Contoh perbaikan N+1 query:**
```python
# Sebelum (N+1 query)
pendaftar_list = Pendaftar.objects.all()
for p in pendaftar_list:
    jumlah_dokumen = p.dokumen_set.count()  # query per-loop

# Sesudah (dioptimasi)
from django.db.models import Count
pendaftar_list = Pendaftar.objects.annotate(jumlah_dokumen=Count('dokumen'))
```

---

## 10. Strategi Code Review

| Aspek yang Direview | Checklist |
|----------------------|-----------|
| Struktur & Modularitas | Logika bisnis tidak bercampur dengan view (dipisah ke `services/`) |
| Penamaan | Variabel & fungsi deskriptif, sesuai `snake_case`/`PascalCase` |
| Duplikasi Kode | Tidak ada logika yang diulang tanpa fungsi/utilitas bersama |
| Keamanan | Tidak ada raw SQL tanpa parameter binding, validasi input ada |
| Dokumentasi | Setiap fungsi punya docstring lengkap (parameter & return) |
| Test Coverage | Fungsi kritis (scoring, ranking) memiliki unit test |

**Contoh before-after refactor (didemokan saat code review):**

```python
# BEFORE — logika bisnis campur dengan view, sulit dites
def form_pendaftaran(request):
    if request.method == 'POST':
        nilai_akademik = float(request.POST['nilai_akademik'])
        nilai_tes = float(request.POST['nilai_tes'])
        skor = (nilai_akademik * 0.6) + (nilai_tes * 0.4)
        # ... simpan ke DB langsung di sini

# AFTER — logika dipisah ke service, view jadi ringkas & fungsi bisa dites terpisah
from pendaftaran.services.scoring import hitung_skor

def form_pendaftaran(request):
    if request.method == 'POST':
        skor = hitung_skor(
            float(request.POST['nilai_akademik']),
            float(request.POST['nilai_tes'])
        )
        # ... simpan ke DB
```

---

## 11. Rencana Skalabilitas

| Aspek | Strategi |
|-------|----------|
| Database | Migrasi dari SQLite ke PostgreSQL saat volume data bertambah besar |
| Query Performance | Indexing kolom yang sering difilter (nisn, status_seleksi, jurusan_pilihan1) |
| Caching | Implementasi Django cache framework untuk data statis (jadwal, FAQ) pada fase lanjutan |
| Horizontal Scaling | Aplikasi stateless (session di DB/cache), memungkinkan multiple instance di belakang load balancer |
| Asynchronous Task | Proses ranking massal (>10.000 data) dapat dipindah ke background task (Celery) pada fase lanjutan |

---

## 12. Deployment (Ringkasan Environment Development)

| Item | Konfigurasi |
|------|-------------|
| Server Development | `python manage.py runserver` (localhost:8000) |
| Environment Variables | Dikelola via `.env` (django-environ) |
| Dependency | `requirements.txt` (Django, pytest-django, django-debug-toolbar, xhtml2pdf) |
| Static Files | `collectstatic` untuk deployment produksi (di luar scope demo) |

---

## 13. Traceability Matrix (Keterkaitan PRD → TRD)

| Requirement PRD | Implementasi Teknis Terkait |
|-------------------|-------------------------------|
| FR-06 s.d. FR-10 (Autentikasi) | Django Auth, app `accounts/` |
| FR-11 s.d. FR-16 (Pendaftaran) | App `pendaftaran/`, model `Pendaftar`, `Dokumen` |
| FR-17 s.d. FR-21 (Seleksi) | `services/scoring.py`, fungsi `hitung_skor()` & `ranking_pendaftar()` |
| FR-22 s.d. FR-27 (Dashboard Admin) | App `dashboard/`, Django Admin, `services/report.py` |
| NFR-01 (Skalabilitas) | Indexing DB, Bagian 11 |
| NFR-02 (Keamanan) | Bagian 8 |
| NFR-03 (Performa) | Profiling, Bagian 9.4 |
| NFR-04 (Maintainability) | Struktur project, Bagian 4 & 10 |
| NFR-05 (Reliabilitas) | Unit & integration test, Bagian 9.1–9.2 |

---

*Dokumen ini merupakan turunan teknis dari PRD_Sistem_Informasi_PMB.md dan menjadi acuan langsung dalam proses coding, code review, debugging, profiling, serta pengujian program.*
