# Product Requirement Document (PRD)
# Sistem Informasi Penerimaan Mahasiswa Baru (PMB)
### Universitas Nusantara Jaya (Studi Kasus Fiktif)

| | |
|---|---|
| **Versi Dokumen** | 1.0 |
| **Tanggal** | 3 Juli 2026 |
| **Disusun oleh** | Analis Program |
| **Status** | Final untuk Asesmen |
| **Tujuan Dokumen** | Uji Kompetensi Analis Program (Analisis Kebutuhan, Perancangan, Implementasi) |

---

## 1. Latar Belakang

Universitas Nusantara Jaya (UNJ — nama fiktif) saat ini masih menggunakan proses penerimaan mahasiswa baru secara manual/semi-manual berbasis formulir kertas dan rekap Excel. Proses ini menimbulkan beberapa masalah:

- Rekap data pendaftar rawan salah input dan duplikasi.
- Proses seleksi/ranking calon mahasiswa dilakukan manual, memakan waktu, dan rawan human error.
- Calon mahasiswa kesulitan mengakses informasi jalur masuk, jadwal, dan status pendaftaran secara real-time.
- Panitia PMB kesulitan menghasilkan laporan rekapitulasi secara cepat dan akurat.

Untuk itu, dibutuhkan **Sistem Informasi PMB berbasis web** yang mampu mendigitalisasi proses pendaftaran, seleksi, hingga pelaporan secara terintegrasi.

---

## 2. Tujuan Produk

1. Menyediakan portal pendaftaran online yang mudah diakses calon mahasiswa.
2. Mengotomatisasi proses perhitungan skor dan perankingan calon mahasiswa berdasarkan kriteria yang ditentukan.
3. Menyediakan dashboard admin untuk mengelola data pendaftar, kuota program studi, dan laporan.
4. Memastikan sistem dibangun dengan praktik rekayasa perangkat lunak yang baik: basis data relasional (SQL), algoritma yang teruji, kode terdokumentasi, serta diuji melalui unit test dan integration test.

---

## 3. Ruang Lingkup (Scope)

### 3.1 Scope yang Dikerjakan (In-Scope)

| No | Modul | Keterangan |
|----|-------|------------|
| 1 | Landing Page & Informasi | Statis/semi-dinamis: profil kampus, jalur masuk, jadwal, biaya, FAQ |
| 2 | Autentikasi & Akun | Register, login, logout, reset password (menggunakan Django Auth) |
| 3 | Modul Pendaftaran | Biodata, data nilai akademik, pilihan program studi, upload dokumen, cetak bukti pendaftaran |
| 4 | Modul Seleksi | Perhitungan skor otomatis, ranking, penentuan status kelulusan (Lulus/Cadangan/Tidak Lulus) |
| 5 | Dashboard Admin | Manajemen data pendaftar, manajemen kuota prodi, export laporan (CSV) |
| 6 | Status Pembayaran (Simplifikasi) | Field status bayar (Lunas/Belum Lunas) yang diubah manual oleh admin |

### 3.2 Scope yang Tidak Dikerjakan (Out-of-Scope)

| No | Modul | Alasan |
|----|-------|--------|
| 1 | Payment Gateway / Virtual Account | Integrasi pihak ketiga, di luar fokus penilaian kompetensi backend |
| 2 | Ujian Berbasis Komputer (CBT) Online | Kompleksitas tinggi, memerlukan modul terpisah |
| 3 | Modul Daftar Ulang Lengkap | Dianggap pengembangan lanjutan (fase 2) |
| 4 | Integrasi PDDIKTI | Memerlukan akses API resmi pihak eksternal |

> **Catatan:** Modul out-of-scope dapat dijelaskan sebagai "rencana pengembangan lanjutan" saat sesi tanya-jawab asesmen.

---

## 4. Target Pengguna (User Roles)

| Role | Deskripsi | Hak Akses Utama |
|------|-----------|------------------|
| **Calon Mahasiswa** | Pengguna publik yang mendaftar | Registrasi akun, isi formulir, upload dokumen, lihat status/pengumuman |
| **Admin PMB** | Panitia penerimaan | Verifikasi data, kelola kuota, generate laporan, atur status pembayaran |
| **Super Admin** | Pengelola sistem | Semua akses admin + manajemen user & konfigurasi jalur masuk |

---

## 5. Kebutuhan Fungsional (Functional Requirements)

### 5.1 Landing Page & Informasi
- FR-01: Sistem menampilkan halaman utama berisi visi-misi, akreditasi institusi & prodi.
- FR-02: Sistem menampilkan daftar jalur masuk (Reguler, Prestasi, KIP-K, Kerjasama).
- FR-03: Sistem menampilkan timeline penting (buka pendaftaran, tes, pengumuman).
- FR-04: Sistem menampilkan estimasi biaya studi (uang pangkal, SPP/UKT).
- FR-05: Sistem menyediakan halaman FAQ dan kontak bantuan.

### 5.2 Autentikasi & Akun
- FR-06: Pengguna dapat mendaftar akun menggunakan NIK, NISN, dan email aktif.
- FR-07: Sistem melakukan validasi keunikan (unique constraint) pada NIK/NISN/email.
- FR-08: Pengguna dapat login menggunakan email dan password.
- FR-09: Pengguna dapat melakukan reset password melalui email.
- FR-10: Password disimpan dalam bentuk hash (tidak plaintext).

### 5.3 Modul Pendaftaran
- FR-11: Pengguna terautentikasi dapat mengisi biodata (nama, TTL, alamat, kontak).
- FR-12: Pengguna dapat mengisi data pendidikan & nilai akademik (asal sekolah, nilai rapor).
- FR-13: Pengguna dapat memilih program studi prioritas (pilihan 1 & 2).
- FR-14: Pengguna dapat mengunggah dokumen (KTP/KK, pas foto, ijazah/SKL) dengan validasi tipe & ukuran file.
- FR-15: Sistem menghasilkan nomor registrasi unik otomatis setiap pendaftaran baru.
- FR-16: Pengguna dapat mengunduh/mencetak Kartu Bukti Pendaftaran dalam format PDF.

### 5.4 Modul Seleksi
- FR-17: Sistem menghitung skor akhir pendaftar berdasarkan formula: `skor_akhir = (nilai_akademik × 0.6) + (nilai_tes × 0.4)`.
- FR-18: Sistem melakukan perankingan otomatis berdasarkan skor akhir per program studi.
- FR-19: Sistem menerapkan aturan tie-breaker apabila terdapat skor sama (diurutkan berdasarkan nilai akademik tertinggi).
- FR-20: Sistem menentukan status akhir (Lulus/Cadangan/Tidak Lulus) berdasarkan kuota program studi.
- FR-21: Pengguna dapat melihat hasil seleksi dengan memasukkan nomor registrasi.

### 5.5 Dashboard Admin
- FR-22: Admin dapat melihat rekapitulasi seluruh data pendaftar dalam bentuk tabel dengan filter (per prodi, status, jalur masuk).
- FR-23: Admin dapat memverifikasi kelengkapan berkas pendaftar.
- FR-24: Admin dapat mengatur kuota masing-masing program studi.
- FR-25: Admin dapat mengubah status pembayaran pendaftar (Lunas/Belum Lunas).
- FR-26: Admin dapat mengekspor data pendaftar ke format CSV/Excel.
- FR-27: Admin dapat menjalankan proses seleksi/ranking secara manual melalui tombol aksi di dashboard.

---

## 6. Kebutuhan Non-Fungsional (Non-Functional Requirements)

| Kode | Kategori | Deskripsi |
|------|----------|-----------|
| NFR-01 | Skalabilitas | Struktur database dan query dirancang menggunakan indexing pada kolom yang sering di-query (nisn, jurusan_id, status) agar tetap responsif saat volume data bertambah |
| NFR-02 | Keamanan | Menggunakan Django ORM (parameterized query) untuk mencegah SQL Injection; password di-hash; CSRF protection aktif |
| NFR-03 | Performa | Waktu respon halaman < 2 detik untuk operasi standar (diverifikasi melalui profiling) |
| NFR-04 | Maintainability | Kode mengikuti coding guideline (PEP8), didokumentasikan dengan docstring, dan dipisah per layer (model-view-service) |
| NFR-05 | Reliabilitas | Fungsi kritis (perhitungan skor, ranking) tercakup dalam unit test dengan syarat lulus 100% sebelum rilis |
| NFR-06 | Usability | Antarmuka responsif, dapat diakses melalui desktop maupun mobile browser |
| NFR-07 | Portabilitas | Aplikasi dapat dijalankan pada environment berbeda menggunakan `requirements.txt` dan file konfigurasi environment |

---

## 7. Model Data (Entity Overview)

| Entitas | Atribut Utama | Relasi |
|---------|----------------|--------|
| **User** (Django Auth) | id, email, password, role | 1—1 dengan Pendaftar |
| **Pendaftar** | id, user_id, nik, nisn, nama, ttl, alamat, no_hp, nilai_akademik, nilai_tes, skor_akhir, status_seleksi, status_bayar, no_registrasi | Many-to-1 dengan Jurusan |
| **Jurusan** | id, nama_jurusan, kuota, akreditasi | 1—Many dengan Pendaftar |
| **JalurMasuk** | id, nama_jalur, deskripsi, periode_mulai, periode_selesai | Many-to-1 dari Pendaftar |
| **Dokumen** | id, pendaftar_id, jenis_dokumen, file_path, status_verifikasi | Many-to-1 dengan Pendaftar |
| **JadwalPenting** | id, nama_kegiatan, tanggal_mulai, tanggal_selesai | - |

> Diagram ERD detail disusun terpisah pada dokumen teknis (`docs/ERD.png`).

---

## 8. Algoritma Utama

### 8.1 Perhitungan Skor
```
skor_akhir = (nilai_akademik * 0.6) + (nilai_tes * 0.4)
```

### 8.2 Proses Ranking & Penentuan Kelulusan
```
1. Ambil seluruh pendaftar per program studi
2. Urutkan (sort) descending berdasarkan skor_akhir
3. Jika skor_akhir sama → urutkan descending berdasarkan nilai_akademik (tie-breaker)
4. Tetapkan status:
   - Peringkat 1 s.d. kuota        -> "Lulus"
   - Peringkat (kuota+1) s.d. (kuota+cadangan) -> "Cadangan"
   - Sisanya                       -> "Tidak Lulus"
```

Kompleksitas algoritma: **O(n log n)** karena didominasi oleh proses sorting.

---

## 9. Rencana Pengujian (Testing Plan)

| Jenis Pengujian | Target | Tools |
|------------------|--------|-------|
| Unit Test | Fungsi `hitung_skor()`, `ranking_pendaftar()`, validasi form | Django TestCase / pytest-django |
| Integration Test | Alur pendaftaran → verifikasi → seleksi → pengumuman | Django TestCase (Client) |
| Debugging | Simulasi bug pada perhitungan skor (tipe data), ditelusuri menggunakan `pdb`/breakpoint | Django Debug Toolbar, pdb |
| Profiling | Analisis waktu eksekusi & jumlah query per halaman | Django Debug Toolbar / cProfile |
| Code Review | Review manual terhadap struktur kode, penamaan variabel, duplikasi kode | Checklist coding guideline internal |

---

## 10. Coding Guidelines (Ringkasan)

- Mengikuti standar **PEP8** untuk penulisan kode Python.
- Penamaan variabel dan fungsi menggunakan `snake_case`, kelas menggunakan `PascalCase`.
- Setiap fungsi wajib memiliki **docstring** (deskripsi, parameter, return value).
- Logika bisnis (algoritma skor/ranking) dipisahkan dari `views.py` ke dalam modul `services/`.
- Tidak ada query SQL mentah tanpa parameter binding (gunakan Django ORM).
- Setiap fitur baru wajib disertai unit test sebelum dianggap selesai.

---

## 11. Batasan (Constraints)

- Waktu pengembangan terbatas (± 3 hari) sehingga fitur pembayaran online dan CBT tidak diimplementasikan penuh.
- Data yang digunakan bersifat **fiktif/dummy** untuk keperluan simulasi dan pengujian, bukan data pendaftar sesungguhnya.
- Aplikasi dijalankan pada environment pengembangan (local server), belum mencakup deployment produksi (load balancer, CDN, dsb).

---

## 12. Kriteria Keberhasilan (Acceptance Criteria)

- [ ] Calon mahasiswa dapat mendaftar, login, dan mengisi formulir pendaftaran dengan sukses.
- [ ] Sistem mampu menghitung skor dan menentukan status kelulusan secara otomatis dan akurat.
- [ ] Admin dapat melihat, memverifikasi, dan mengekspor data pendaftar.
- [ ] Seluruh fungsi kritis memiliki unit test dengan status **pass**.
- [ ] Minimal 1 skenario integration test (alur pendaftaran-seleksi) berjalan sukses.
- [ ] Dokumentasi kode (docstring & README) tersedia lengkap.
- [ ] Hasil profiling menunjukkan tidak ada N+1 query pada halaman dashboard admin.

---

## 13. Lampiran

- Struktur folder project: lihat `README.md`
- ERD: `docs/ERD.png`
- Coding Guidelines lengkap: `docs/coding_guidelines.md`
- Skrip pengujian: folder `tests/`

---

*Dokumen ini disusun sebagai bagian dari tugas Uji Kompetensi Analis Program dan dapat disesuaikan seiring perkembangan implementasi.*
