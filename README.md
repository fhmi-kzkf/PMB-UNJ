# Sistem Informasi Penerimaan Mahasiswa Baru (PMB)

Aplikasi PMB berbasis web (Django) ini dirancang sebagai pemenuhan tugas sertifikasi **Analis Program**. Aplikasi ini mencakup manajemen pendaftaran mahasiswa, seleksi otomatis, validasi dokumen, hingga dasbor analitik.

## ✨ Fitur Utama

### 🎓 Sisi Calon Mahasiswa
- **Pendaftaran Berjenjang:** Formulir 5 tahap (Biodata, Akademik, Pilihan Prodi, Data Ortu, dan Upload Berkas) yang *user-friendly*.
- **Auto-Save Draft:** Integrasi `localStorage` memastikan isian tidak hilang saat halaman di-refresh.
- **Cek Status & Bukti:** Pendaftar dapat melihat status seleksi (Menunggu/Lulus/Gagal) dan mencetak bukti resi kelulusan.

### 🛡️ Sisi Admin (Dasbor)
- **Tinjauan Komprehensif:** Rekap data pelamar berdasarkan jurusan dan status pendaftaran.
- **Validasi Berkas & ACC Instan:** Admin dapat melihat berkas (KTP, Ijazah, dll) dan melakukan ACC otomatis jika syarat terpenuhi.
- **Penilaian Otomatis (Auto-Scoring):** Algoritma seleksi yang menghitung bobot Nilai Akademik (60%) dan Nilai Tes CBT (40%).
- **Manajemen Pembayaran:** Status pembayaran (Lunas/Belum Lunas).

## 🛠️ Standar Kelulusan Sertifikasi Terpenuhi

Aplikasi ini mendemonstrasikan implementasi 9 kriteria asesmen sertifikasi Analis Program:
1. **Analisis Skalabilitas:** Menggunakan arsitektur MVT (Model-View-Template) yang *scalable* di Django.
2. **Penggunaan SQL:** Eksploitasi ORM Django untuk agregasi data kompleks.
3. **Akses Basis Data:** Penggunaan relasi database (MySQL/SQLite3) yang aman.
4. **Algoritma Pemrograman:** Logika *scoring* (pembobotan nilai) untuk pemeringkatan (*ranking*) pelamar.
5. **Pembuatan Dokumen Kode:** Penerapan *docstring* PEP-8 di seluruh modul penting.
6. **Debugging:** Konfigurasi *logging* yang secara otomatis merekam aktivitas dan *error* sistem ke `debug.log`.
7. **Profiling Program:** Terintegrasi dengan `django-debug-toolbar` untuk memonitor kueri SQL dan waktu eksekusi.
8. **Code Review:** Pengembangan kolaboratif yang sistematis.
9. **Pengujian (Unit & Integration Test):** Menggunakan `pytest` untuk memvalidasi algoritma skor, formulir pendaftaran, dan skenario pendaftaran *end-to-end*.

## 🚀 Cara Menjalankan

1. **Buat Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Untuk Windows
   ```
2. **Instal Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Migrasi Database:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Jalankan Server:**
   ```bash
   python manage.py runserver
   ```
5. Akses aplikasi melalui browser di `http://127.0.0.1:8000`.

## 🧪 Cara Menjalankan Pengujian

Jalankan perintah berikut di dalam terminal untuk mengeksekusi semua *Unit Test* dan *Integration Test*:
```bash
pytest tests/ -v
```

---
*Proyek ini merupakan demonstrasi keahlian pemrograman, logika, dan penyelesaian masalah di level industri.*
