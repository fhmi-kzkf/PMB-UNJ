"""
Management command untuk mengisi database dengan data dummy.
Berguna untuk simulasi demo aplikasi.
"""

import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from pendaftaran.models import Jurusan, JalurMasuk, Pendaftar, JadwalPenting
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Seeding database dengan data fiktif untuk simulasi PMB'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Memulai proses seeding data...'))

        # 1. Clear existing data to avoid conflicts
        JadwalPenting.objects.all().delete()
        Pendaftar.objects.all().delete()
        Jurusan.objects.all().delete()
        JalurMasuk.objects.all().delete()
        User.objects.filter(is_superuser=False).delete() # Keep superusers if any
        self.stdout.write('Data lama dibersihkan.')

        # 2. Seed Jadwal Penting
        JadwalPenting.objects.create(
            nama_kegiatan='Pendaftaran Online Gelombang 1',
            tanggal_mulai=date(2026, 1, 15),
            tanggal_selesai=date(2026, 3, 30)
        )
        JadwalPenting.objects.create(
            nama_kegiatan='Tes Seleksi Berbasis Komputer',
            tanggal_mulai=date(2026, 4, 15),
            tanggal_selesai=date(2026, 4, 20)
        )
        JadwalPenting.objects.create(
            nama_kegiatan='Pengumuman Kelulusan',
            tanggal_mulai=date(2026, 5, 10),
            tanggal_selesai=date(2026, 5, 10)
        )
        JadwalPenting.objects.create(
            nama_kegiatan='Daftar Ulang dan Pembayaran',
            tanggal_mulai=date(2026, 5, 12),
            tanggal_selesai=date(2026, 5, 25)
        )
        self.stdout.write('Data jadwal berhasil dibuat.')

        # 3. Seed Jalur Masuk
        jalur_list = [
            JalurMasuk.objects.create(nama_jalur='Reguler', deskripsi='Jalur pendaftaran umum menggunakan nilai rapor dan ujian tulis.'),
            JalurMasuk.objects.create(nama_jalur='Prestasi', deskripsi='Jalur khusus bagi siswa berprestasi akademik maupun non-akademik (min. tingkat kota/kabupaten).'),
            JalurMasuk.objects.create(nama_jalur='KIP-K', deskripsi='Jalur beasiswa penuh dari pemerintah untuk mahasiswa dari keluarga kurang mampu.'),
            JalurMasuk.objects.create(nama_jalur='Kerjasama', deskripsi='Jalur khusus instansi/pemerintah daerah yang telah bekerja sama dengan universitas.')
        ]
        self.stdout.write('Data jalur masuk berhasil dibuat.')

        # 4. Seed Jurusan
        jurusan_data = [
            (
                'Teknik Informatika', 
                'A', 
                10, 
                5,
                'Fokus pada pengembangan perangkat lunak, kecerdasan buatan (AI), cloud computing, dan rekayasa data untuk solusi industri digital masa kini.',
                'Struktur Data, Desain Algoritma, Pemrograman Web & Mobile, Machine Learning, Cloud Computing, Teori Graf',
                'Software Engineer, AI Engineer, Fullstack Web Developer, Machine Learning Specialist'
            ),
            (
                'Sistem Informasi', 
                'A', 
                8, 
                4,
                'Menggabungkan dunia teknologi dengan bisnis, mengelola tata kelola arsitektur enterprise, serta menganalisis kebutuhan IT bagi proses bisnis organisasi.',
                'Analisis & Desain Sistem, Basis Data, Manajemen Proyek TI, Arsitektur Enterprise, Business Intelligence, E-Commerce',
                'IT Business Analyst, System Analyst, IT Consultant, Database Administrator'
            ),
            (
                'Rekayasa Perangkat Lunak', 
                'A', 
                8, 
                4,
                'Mempelajari prinsip rekayasa dalam siklus pembuatan software skala industri, berfokus pada keandalan sistem, pengujian perangkat lunak, dan DevOps.',
                'Software Architecture, Software Testing & Quality Assurance, DevOps, Agile & Scrum Methodologies, Cloud Native Applications',
                'QA Engineer, DevOps Specialist, Software Architect'
            ),
            (
                'Teknologi Informasi', 
                'B', 
                10, 
                5,
                'Fokus pada instalasi, pengelolaan infrastruktur IT, keamanan sistem operasi, jaringan komputer, serta manajemen integrasi sistem terpadu.',
                'Administrasi Jaringan & Server, Keamanan Jaringan, Cloud Computing, Virtualisasi, System Administration, IoT Foundations',
                'Network Engineer, System Administrator, Cloud Infrastructure Engineer'
            ),
            (
                'Keamanan Siber', 
                'A', 
                6, 
                3,
                'Mempelajari cara melindungi aset digital organisasi dengan mendeteksi celah keamanan, melakukan enkripsi data, dan investigasi forensik digital.',
                'Ethical Hacking & Pentest, Kriptografi, Digital Forensics, Network Security, Incident Response, Risk Management',
                'Security Analyst, Penetration Tester, Cybersecurity Consultant, Digital Forensic Investigator'
            ),
            (
                'Sains Data', 
                'B', 
                8, 
                4,
                'Mengolah dan menganalisis data dalam skala raksasa (Big Data) menggunakan pemodelan matematika, statistik, serta pemrograman AI untuk menghasilkan analisis bisnis yang cerdas.',
                'Statistika untuk Sains Data, Big Data Analytics, Visualisasi Data, Data Mining, Pemrograman Python/R, Deep Learning',
                'Data Analyst, Data Scientist, Data Engineer, Business Intelligence Developer'
            ),
        ]
        jurusan_list = []
        for nama, akreditasi, kuota, cadangan, deskripsi, materi, prospek in jurusan_data:
            jurusan_list.append(
                Jurusan.objects.create(
                    nama_jurusan=nama, akreditasi=akreditasi,
                    kuota=kuota, kuota_cadangan=cadangan,
                    deskripsi=deskripsi, materi_pembelajaran=materi,
                    prospek_karir=prospek
                )
            )
        self.stdout.write('Data program studi berhasil dibuat.')

        # 5. Seed Users (Admin)
        if not User.objects.filter(username='adminpmb').exists():
            admin = User.objects.create_user('adminpmb', 'admin@pmb.unj.ac.id', 'admin123')
            admin.first_name = 'Admin'
            admin.last_name = 'Utama'
            admin.save()
            admin.profile.role = 'admin_pmb'
            admin.profile.save()
            self.stdout.write('Akun admin berhasil dibuat (user: adminpmb, pass: admin123).')

        # 6. Seed Pendaftar Dummy
        first_names = ['Budi', 'Siti', 'Andi', 'Dewi', 'Eko', 'Rina', 'Fajar', 'Nina', 'Gilang', 'Putri']
        last_names = ['Santoso', 'Wijaya', 'Kusuma', 'Pratama', 'Lestari', 'Saputra', 'Sari', 'Hidayat', 'Nugroho', 'Wulandari']
        sekolah = ['SMA N 1', 'SMA N 2', 'SMA N 3', 'SMK N 1', 'SMK N 2']
        kota = ['Jakarta', 'Bandung', 'Surabaya', 'Semarang', 'Yogyakarta']

        from pendaftaran.services.scoring import generate_no_registrasi, hitung_skor

        for i in range(1, 21):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            email = f"calon{i}@example.com"
            nik = f"320101010101{str(i).zfill(4)}"
            nisn = f"001234{str(i).zfill(4)}"
            
            # Create user
            user = User.objects.create_user(email, email, 'siswa123')
            user.first_name = fname
            user.last_name = lname
            user.save()
            user.profile.role = 'calon_mahasiswa'
            user.profile.nik = nik
            user.profile.nisn = nisn
            user.profile.save()

            # Create pendaftar
            j1 = random.choice(jurusan_list)
            j2 = random.choice([j for j in jurusan_list if j.id != j1.id] + [None])
            
            n_akademik = round(random.uniform(70.0, 95.0), 2)
            n_tes = round(random.uniform(65.0, 98.0), 2)
            
            Pendaftar.objects.create(
                user=user,
                no_registrasi=generate_no_registrasi(),
                nik=nik,
                nisn=nisn,
                nama_lengkap=f"{fname} {lname}",
                email=email,
                tempat_lahir=random.choice(kota),
                tanggal_lahir=date(2008, random.randint(1,12), random.randint(1,28)),
                alamat=f"Jl. Pendidikan No. {i}, {random.choice(kota)}",
                no_hp=f"0812345678{str(i).zfill(2)}",
                asal_sekolah=f"{random.choice(sekolah)} {random.choice(kota)}",
                jurusan_sekolah=random.choice(['IPA', 'IPS', 'Kejuruan']),
                tahun_lulus=random.choice([2024, 2025, 2026]),
                jurusan_pilihan1=j1,
                jurusan_pilihan2=j2,
                jalur_masuk=random.choice(jalur_list),
                jenis_kelas=random.choice(['reguler', 'karyawan']),
                nama_ayah=f"Ayah {lname}",
                nama_ibu=f"Ibu {fname}",
                no_hp_ortu=f"0821234567{str(i).zfill(2)}",
                pekerjaan_ortu=random.choice(['pns', 'swasta', 'wiraswasta', 'buruh']),
                penghasilan_ortu=random.choice(['1jt_3jt', '3jt_5jt', '5jt_10jt']),
                nilai_akademik=n_akademik,
                nilai_tes=n_tes,
                skor_akhir=hitung_skor(n_akademik, n_tes),
                status_seleksi='menunggu',
                status_bayar=random.choice(['lunas', 'belum_lunas']) if random.random() > 0.7 else 'belum_lunas'
            )

        self.stdout.write(self.style.SUCCESS('Berhasil membuat 20 data pendaftar dummy.'))
        self.stdout.write(self.style.SUCCESS('SEEDING SELESAI!'))
