"""
Integration tests untuk alur pendaftaran dari registrasi hingga cek hasil.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from pendaftaran.models import Pendaftar, Jurusan, JalurMasuk
from pendaftaran.services.scoring import jalankan_seleksi


class PendaftaranFlowTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.j1 = Jurusan.objects.create(nama_jurusan='Informatika', kuota=1)
        self.j2 = Jurusan.objects.create(nama_jurusan='Sistem Informasi', kuota=2)
        self.jalur = JalurMasuk.objects.create(nama_jalur='Reguler')

    def test_full_registration_flow(self):
        # 1. Register
        register_data = {
            'nama_lengkap': 'Calon Mahasiswa',
            'email': 'calon@test.com',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        response = self.client.post(reverse('accounts:register'), register_data)
        self.assertEqual(response.status_code, 302) # Redirect to login on success
        
        user = User.objects.get(email='calon@test.com')
        self.assertIsNotNone(user)

        # 2. Login
        login_data = {
            'username': 'calon@test.com',
            'password': 'password123'
        }
        response = self.client.post(reverse('accounts:login'), login_data)
        self.assertEqual(response.status_code, 302) # Redirect to status/form

        # 3. Submit Pendaftaran Form
        from django.core.files.uploadedfile import SimpleUploadedFile
        file_content = b'dummy content'
        pendaftaran_data = {
            'nama_lengkap': 'Calon Mahasiswa',
            'nik': '3201010101010001',
            'nisn': '0012345678',
            'tempat_lahir': 'Jakarta',
            'tanggal_lahir': '2008-01-01',
            'alamat': 'Jl. Pendidikan',
            'no_hp': '081234567890',
            'email': 'calon@test.com',
            'asal_sekolah': 'SMA N 1',
            'jurusan_sekolah': 'IPA',
            'tahun_lulus': 2026,
            'jurusan_pilihan1': self.j1.id,
            'jurusan_pilihan2': self.j2.id,
            'jalur_masuk': self.jalur.id,
            'jenis_kelas': 'reguler',
            'nilai_akademik': '80.00',
            'nilai_tes': '90.00',
            'nama_ayah': 'Ayah',
            'nama_ibu': 'Ibu',
            'no_hp_ortu': '08123456789',
            'pekerjaan_ortu': 'swasta',
            'penghasilan_ortu': '3jt_5jt',
            'file_pasfoto': SimpleUploadedFile("pasfoto.jpg", file_content, content_type="image/jpeg"),
            'file_ktp': SimpleUploadedFile("ktp.jpg", file_content, content_type="image/jpeg"),
            'file_kk': SimpleUploadedFile("kk.jpg", file_content, content_type="image/jpeg"),
            'file_ijazah': SimpleUploadedFile("ijazah.pdf", file_content, content_type="application/pdf"),
        }
        response = self.client.post(reverse('pendaftaran:form'), pendaftaran_data)
        self.assertEqual(response.status_code, 302) # Redirect to upload on success

        # 4. Check DB for Pendaftar and Auto-Score
        pendaftar = Pendaftar.objects.get(nisn='0012345678')
        self.assertIsNotNone(pendaftar)
        self.assertTrue(pendaftar.no_registrasi.startswith('PMB-'))
        
        # Saat mendaftar, nilai_tes dipaksa 0 oleh sistem. 80*0.6 + 0 = 48.00
        self.assertEqual(float(pendaftar.skor_akhir), 48.0)
        self.assertEqual(pendaftar.status_seleksi, 'menunggu')

        # Simulasi Admin menginput nilai CBT
        from pendaftaran.services.scoring import hitung_skor
        pendaftar.nilai_tes = 90.0
        pendaftar.skor_akhir = hitung_skor(pendaftar.nilai_akademik, pendaftar.nilai_tes)
        pendaftar.save()
        
        # 80*0.6 + 90*0.4 = 48 + 36 = 84.00
        self.assertEqual(float(pendaftar.skor_akhir), 84.0)

        # 5. Run Selection (Admin action simulation)
        # Create a competitor to test ranking
        user2 = User.objects.create_user('competitor@test.com', 'competitor@test.com', 'pass')
        Pendaftar.objects.create(
            user=user2,
            no_registrasi='PMB-2026-COMPETITOR',
            nik='111', nisn='111', nama_lengkap='Competitor',
            jurusan_pilihan1=self.j1, jalur_masuk=self.jalur,
            nilai_akademik=90, nilai_tes=95, skor_akhir=92.0 # Higher score
        )
        
        # Trigger selection for j1 (kuota=1)
        jalankan_seleksi(self.j1.id)

        # 6. Check Result (Public view)
        pendaftar.refresh_from_db()
        self.assertEqual(pendaftar.status_seleksi, 'tidak_lulus') # Lost to competitor

        response = self.client.get(f"{reverse('pendaftaran:hasil')}?no_registrasi={pendaftar.no_registrasi}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TIDAK LULUS')
