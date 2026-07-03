# Database Schema & Application Flow
# Sistem Informasi Penerimaan Mahasiswa Baru (PMB)
### Universitas Nusantara Jaya (Studi Kasus Fiktif)

| | |
|---|---|
| **Versi Dokumen** | 1.0 |
| **Tanggal** | 3 Juli 2026 |
| **Disusun oleh** | Analis Program |
| **Dokumen Acuan** | PRD_Sistem_Informasi_PMB.md, TRD_Sistem_Informasi_PMB.md |
| **Status** | Final untuk Asesmen |

---

## 1. Database Schema

### 1.1 Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    AUTH_USER ||--|| PENDAFTAR : "memiliki"
    JURUSAN ||--o{ PENDAFTAR : "pilihan1"
    JURUSAN ||--o{ PENDAFTAR : "pilihan2"
    JALUR_MASUK ||--o{ PENDAFTAR : "digunakan oleh"
    PENDAFTAR ||--o{ DOKUMEN : "mengunggah"
    JADWAL_PENTING {
        int id PK
        string nama_kegiatan
        date tanggal_mulai
        date tanggal_selesai
    }

    AUTH_USER {
        int id PK
        string email UK
        string password
        string role
    }

    JURUSAN {
        int id PK
        string nama_jurusan
        string akreditasi
        int kuota
        int kuota_cadangan
    }

    JALUR_MASUK {
        int id PK
        string nama_jalur
        text deskripsi
        date periode_mulai
        date periode_selesai
    }

    PENDAFTAR {
        int id PK
        int user_id FK
        string no_registrasi UK
        string nik UK
        string nisn UK
        string nama_lengkap
        string tempat_lahir
        date tanggal_lahir
        text alamat
        string no_hp
        int jurusan_pilihan1 FK
        int jurusan_pilihan2 FK
        int jalur_masuk_id FK
        decimal nilai_akademik
        decimal nilai_tes
        decimal skor_akhir
        string status_seleksi
        string status_bayar
        timestamp created_at
    }

    DOKUMEN {
        int id PK
        int pendaftar_id FK
        string jenis_dokumen
        string file_path
        string status_verifikasi
        timestamp uploaded_at
    }
```

> Catatan: `AUTH_USER` merupakan tabel bawaan Django Auth (`auth_user`), tidak dibuat ulang secara manual — hanya diperluas melalui field `role` (via model `Profile`/`OneToOneField` sesuai app `accounts/`).

### 1.2 Detail Tabel

#### a. `jurusan`

| Kolom | Tipe | Constraint | Keterangan |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | |
| nama_jurusan | VARCHAR(100) | NOT NULL | |
| akreditasi | VARCHAR(5) | | contoh: A, B, Unggul |
| kuota | INTEGER | NOT NULL, DEFAULT 0 | kuota utama (Lulus) |
| kuota_cadangan | INTEGER | NOT NULL, DEFAULT 0 | kuota tambahan (Cadangan) |

#### b. `jalur_masuk`

| Kolom | Tipe | Constraint | Keterangan |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | |
| nama_jalur | VARCHAR(50) | NOT NULL | Reguler / Prestasi / KIP-K / Kerjasama |
| deskripsi | TEXT | | |
| periode_mulai | DATE | | |
| periode_selesai | DATE | | |

#### c. `pendaftar`

| Kolom | Tipe | Constraint | Keterangan |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | |
| user_id | INTEGER | FK → auth_user(id), UNIQUE, NOT NULL | relasi 1—1 dengan akun login |
| no_registrasi | VARCHAR(20) | UNIQUE, NOT NULL | digenerate otomatis saat submit (FR-15) |
| nik | VARCHAR(16) | UNIQUE, NOT NULL | |
| nisn | VARCHAR(10) | UNIQUE, NOT NULL | **INDEX** (idx_pendaftar_nisn) |
| nama_lengkap | VARCHAR(150) | NOT NULL | |
| tempat_lahir | VARCHAR(100) | | |
| tanggal_lahir | DATE | | |
| alamat | TEXT | | |
| no_hp | VARCHAR(15) | | |
| jurusan_pilihan1 | INTEGER | FK → jurusan(id), NOT NULL | **INDEX** (idx_pendaftar_jurusan1) |
| jurusan_pilihan2 | INTEGER | FK → jurusan(id), NULLABLE | |
| jalur_masuk_id | INTEGER | FK → jalur_masuk(id), NOT NULL | |
| nilai_akademik | DECIMAL(5,2) | | skala 0–100 |
| nilai_tes | DECIMAL(5,2) | | skala 0–100 |
| skor_akhir | DECIMAL(5,2) | | hasil `hitung_skor()`, dihitung otomatis |
| status_seleksi | VARCHAR(20) | DEFAULT 'menunggu' | menunggu \| lulus \| cadangan \| tidak_lulus — **INDEX** (idx_pendaftar_status) |
| status_bayar | VARCHAR(15) | DEFAULT 'belum_lunas' | lunas \| belum_lunas |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |

#### d. `dokumen`

| Kolom | Tipe | Constraint | Keterangan |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | |
| pendaftar_id | INTEGER | FK → pendaftar(id), NOT NULL | |
| jenis_dokumen | VARCHAR(30) | NOT NULL | ktp \| kk \| pas_foto \| ijazah |
| file_path | VARCHAR(255) | NOT NULL | validasi tipe (pdf/jpg/png) & maks. 2MB |
| status_verifikasi | VARCHAR(20) | DEFAULT 'belum_diverifikasi' | belum_diverifikasi \| terverifikasi \| ditolak |
| uploaded_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |

#### e. `jadwal_penting`

| Kolom | Tipe | Constraint | Keterangan |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | |
| nama_kegiatan | VARCHAR(150) | NOT NULL | ditampilkan di landing page (FR-03) |
| tanggal_mulai | DATE | | |
| tanggal_selesai | DATE | | |

### 1.3 Ringkasan Indexing (NFR-01)

| Index | Tabel.Kolom | Tujuan |
|---|---|---|
| idx_pendaftar_nisn | pendaftar.nisn | validasi unik & pencarian cepat saat verifikasi |
| idx_pendaftar_jurusan1 | pendaftar.jurusan_pilihan1 | mempercepat query ranking per jurusan |
| idx_pendaftar_status | pendaftar.status_seleksi | mempercepat filter dashboard admin |

### 1.4 Aturan Integritas Data

- `user_id`, `nik`, `nisn`, `no_registrasi`, `email` (`auth_user.email`) bersifat **UNIQUE** — mencegah duplikasi pendaftar (FR-07).
- `jurusan_pilihan1` wajib diisi, `jurusan_pilihan2` opsional.
- Penghapusan `jurusan` atau `jalur_masuk` yang masih direferensikan `pendaftar` dibatasi (`ON DELETE RESTRICT`) agar riwayat pendaftaran tidak rusak.
- Penghapusan `pendaftar` akan menghapus turunan `dokumen` (`ON DELETE CASCADE`).

---

## 2. Application Flow

### 2.1 Peta Alur Umum per Role

```mermaid
flowchart TD
    subgraph Publik
        A[Landing Page] --> B{Punya Akun?}
    end

    subgraph "Calon Mahasiswa"
        B -- Belum --> C[Register: NIK, NISN, Email]
        C --> D[Login]
        B -- Sudah --> D
        D --> E[Isi Formulir Pendaftaran<br/>Biodata + Nilai Akademik]
        E --> F[Pilih Prodi 1 & 2]
        F --> G[Upload Dokumen<br/>KTP/KK, Foto, Ijazah]
        G --> H[Sistem Generate<br/>No. Registrasi]
        H --> I[Cetak Bukti Pendaftaran PDF]
        I --> J[Cek Status via No. Registrasi]
    end

    subgraph "Admin PMB"
        K[Login Admin] --> L[Dashboard Rekap Pendaftar]
        L --> M[Verifikasi Kelengkapan Dokumen]
        L --> N[Atur Kuota Prodi]
        M --> O[Jalankan Proses Seleksi/Ranking]
        O --> P[Update Status Bayar]
        L --> Q[Export Laporan CSV]
    end

    O -.-> J
```

### 2.2 Alur Detail: Registrasi & Pendaftaran (Calon Mahasiswa)

```mermaid
sequenceDiagram
    actor U as Calon Mahasiswa
    participant W as Django Views (accounts/)
    participant DB as Database

    U->>W: Register (NIK, NISN, email, password)
    W->>DB: Cek unique constraint (NIK/NISN/email)
    alt data sudah ada
        DB-->>W: Konflik unik
        W-->>U: Tampilkan error validasi
    else data valid
        DB-->>W: OK
        W->>DB: Simpan user (password ter-hash PBKDF2)
        W-->>U: Redirect ke Login
    end

    U->>W: Login (email, password)
    W->>DB: Verifikasi kredensial
    W-->>U: Session aktif → redirect ke Form Pendaftaran

    U->>W: Submit Form Pendaftaran (biodata, nilai, pilihan prodi)
    W->>W: Validasi form (tipe data, field wajib)
    W->>DB: Simpan data Pendaftar + generate no_registrasi unik
    W-->>U: Redirect ke halaman Upload Dokumen

    U->>W: Upload dokumen (KTP/KK, foto, ijazah)
    W->>W: Validasi tipe file & ukuran (≤2MB)
    W->>DB: Simpan record Dokumen (status: belum_diverifikasi)
    W-->>U: Tampilkan Bukti Pendaftaran (cetak PDF)
```

### 2.3 Alur Detail: Proses Seleksi (Admin → Sistem)

```mermaid
sequenceDiagram
    actor A as Admin PMB
    participant D as Dashboard Views
    participant S as services/scoring.py
    participant DB as Database

    A->>D: Klik "Jalankan Seleksi"
    D->>DB: Ambil seluruh Pendaftar per Jurusan
    DB-->>D: List pendaftar (nilai_akademik, nilai_tes)

    loop setiap pendaftar
        D->>S: hitung_skor(nilai_akademik, nilai_tes)
        S-->>D: skor_akhir
    end

    D->>S: ranking_pendaftar(list, kuota, kuota_cadangan)
    S->>S: Sort descending skor_akhir (tie-breaker: nilai_akademik)
    S->>S: Tetapkan status: lulus / cadangan / tidak_lulus
    S-->>D: List pendaftar dengan status_seleksi

    D->>DB: Update status_seleksi & skor_akhir per pendaftar
    DB-->>D: OK
    D-->>A: Tampilkan ringkasan hasil seleksi
```

### 2.4 State Diagram: `status_seleksi`

```mermaid
stateDiagram-v2
    [*] --> menunggu: Pendaftaran disubmit
    menunggu --> lulus: Ranking ≤ kuota utama
    menunggu --> cadangan: kuota < Ranking ≤ (kuota + kuota_cadangan)
    menunggu --> tidak_lulus: Ranking > (kuota + kuota_cadangan)
    lulus --> [*]
    cadangan --> [*]
    tidak_lulus --> [*]
```

### 2.5 State Diagram: `status_verifikasi` (Dokumen) & `status_bayar`

```mermaid
stateDiagram-v2
    [*] --> belum_diverifikasi: Dokumen diunggah
    belum_diverifikasi --> terverifikasi: Admin verifikasi (valid)
    belum_diverifikasi --> ditolak: Admin verifikasi (tidak valid)
    ditolak --> belum_diverifikasi: Pendaftar unggah ulang

    [*] --> belum_lunas: Pendaftar dinyatakan Lulus
    belum_lunas --> lunas: Admin ubah manual (FR-25)
```

### 2.6 Page Flow — Sisi Publik / Calon Mahasiswa

| Langkah | Halaman/Endpoint | Auth | Aksi |
|---|---|---|---|
| 1 | `GET /` | Publik | Lihat info kampus, jalur masuk, jadwal, biaya, FAQ |
| 2 | `GET/POST /accounts/register/` | Publik | Buat akun (NIK, NISN, email) |
| 3 | `GET/POST /accounts/login/` | Publik | Login |
| 4 | `GET/POST /pendaftaran/form/` | Login | Isi biodata, nilai, pilih prodi |
| 5 | `POST /pendaftaran/upload/` | Login | Upload dokumen |
| 6 | `GET /pendaftaran/bukti/<no_registrasi>/` | Login | Cetak bukti pendaftaran (PDF) |
| 7 | `GET /pendaftaran/hasil/<no_registrasi>/` | Publik (dgn no. reg) | Cek hasil seleksi |
| 8 | `POST /accounts/logout/` | Login | Logout |

### 2.7 Page Flow — Sisi Admin PMB / Super Admin

| Langkah | Halaman/Endpoint | Auth | Aksi |
|---|---|---|---|
| 1 | `GET /dashboard/` | Admin | Rekap statistik pendaftar |
| 2 | `GET /dashboard/pendaftar/` | Admin | List & filter (prodi, status, jalur) |
| 3 | `POST /dashboard/verifikasi/<id>/` | Admin | Verifikasi kelengkapan dokumen |
| 4 | (Kelola kuota prodi via Django Admin / dashboard) | Admin/Super Admin | Atur `kuota` & `kuota_cadangan` |
| 5 | `POST /dashboard/jalankan-seleksi/` | Admin | Trigger `ranking_pendaftar()` |
| 6 | `POST /dashboard/verifikasi/<id>/` (status_bayar) | Admin | Update status pembayaran manual |
| 7 | `GET /dashboard/export/csv/` | Admin | Export laporan CSV |
| — | Manajemen user & konfigurasi jalur masuk | Super Admin | Akses tambahan di luar Admin PMB |

### 2.8 Ringkasan Traceability Flow → FR/NFR

| Bagian Flow | FR/NFR Terkait |
|---|---|
| Registrasi & Login | FR-06 s.d. FR-10, NFR-02 |
| Form Pendaftaran & Upload Dokumen | FR-11 s.d. FR-16, NFR-02 (validasi file) |
| Proses Seleksi & Ranking | FR-17 s.d. FR-21, NFR-05 (unit test 100%) |
| Dashboard Admin & Export | FR-22 s.d. FR-27, NFR-01 (indexing), NFR-03 (performa) |

---

*Dokumen ini disusun berdasarkan `PRD_Sistem_Informasi_PMB.md` dan `TRD_Sistem_Informasi_PMB.md` sebagai referensi implementasi database dan alur aplikasi.*
