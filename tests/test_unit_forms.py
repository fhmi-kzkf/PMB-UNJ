"""
Unit tests untuk validasi form.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.forms import RegistrationForm
from accounts.models import Profile
from pendaftaran.forms import PendaftaranForm, DokumenUploadForm
from pendaftaran.models import Jurusan, JalurMasuk


class RegistrationFormTest(TestCase):

    def setUp(self):
        # Create an existing user to test unique constraints
        self.user = User.objects.create_user('test@test.com', 'test@test.com', 'password123')
        # Create profile since signal might not be connected in tests depending on setup
        if not hasattr(self.user, 'profile'):
            Profile.objects.create(user=self.user, nik='1234567890123456', nisn='1234567890')
        else:
            self.user.profile.nik = '1234567890123456'
            self.user.profile.nisn = '1234567890'
            self.user.profile.save()

    def test_valid_form(self):
        data = {
            'nama_lengkap': 'Budi Santoso',
            'email': 'budi@test.com',
            'nik': '3201010101010001',
            'nisn': '0012345678',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        form = RegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_duplicate_email(self):
        data = {
            'nama_lengkap': 'Budi Santoso',
            'email': 'test@test.com', # Already exists
            'nik': '3201010101010001',
            'nisn': '0012345678',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        data = {
            'nama_lengkap': 'Budi Santoso',
            'email': 'budi@test.com',
            'nik': '3201010101010001',
            'nisn': '0012345678',
            'password': 'password123',
            'password_confirm': 'password321' # Mismatch
        }
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class PendaftaranFormTest(TestCase):

    def setUp(self):
        self.j1 = Jurusan.objects.create(nama_jurusan='Informatika', kuota=10)
        self.j2 = Jurusan.objects.create(nama_jurusan='Sistem Informasi', kuota=10)
        self.jalur = JalurMasuk.objects.create(nama_jalur='Reguler')

    def test_valid_pendaftaran_form(self):
        data = {
            'nama_lengkap': 'Budi',
            'nik': '3201010101010001',
            'nisn': '0012345678',
            'tempat_lahir': 'Jakarta',
            'tanggal_lahir': '2008-01-01',
            'alamat': 'Jl. Sudirman',
            'no_hp': '081234567890',
            'email': 'budi@test.com',
            'asal_sekolah': 'SMA N 1',
            'jurusan_sekolah': 'IPA',
            'tahun_lulus': 2026,
            'jurusan_pilihan1': self.j1.id,
            'jurusan_pilihan2': self.j2.id,
            'jalur_masuk': self.jalur.id,
            'jenis_kelas': 'reguler',
            'nilai_akademik': 85.5,
            'nilai_tes': 90.0,
            'nama_ayah': 'Ayah',
            'nama_ibu': 'Ibu',
            'no_hp_ortu': '08123456789',
            'pekerjaan_ortu': 'swasta',
            'penghasilan_ortu': '3jt_5jt',
        }
        file_content = b'test content'
        file_data = {
            'file_pasfoto': SimpleUploadedFile("pasfoto.jpg", file_content, content_type="image/jpeg"),
            'file_ktp': SimpleUploadedFile("ktp.jpg", file_content, content_type="image/jpeg"),
            'file_kk': SimpleUploadedFile("kk.jpg", file_content, content_type="image/jpeg"),
            'file_ijazah': SimpleUploadedFile("ijazah.pdf", file_content, content_type="application/pdf"),
        }
        form = PendaftaranForm(data=data, files=file_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_same_jurusan_error(self):
        data = {
            'nama_lengkap': 'Budi',
            'nik': '3201010101010001',
            'nisn': '0012345678',
            'tempat_lahir': 'Jakarta',
            'tanggal_lahir': '2008-01-01',
            'alamat': 'Jl. Sudirman',
            'no_hp': '081234567890',
            'email': 'budi@test.com',
            'asal_sekolah': 'SMA N 1',
            'jurusan_sekolah': 'IPA',
            'tahun_lulus': 2026,
            'jurusan_pilihan1': self.j1.id,
            'jurusan_pilihan2': self.j1.id, # Same as pilihan 1
            'jalur_masuk': self.jalur.id,
            'jenis_kelas': 'reguler',
            'nilai_akademik': 85.5,
            'nilai_tes': 90.0,
            'nama_ayah': 'Ayah',
            'nama_ibu': 'Ibu',
            'no_hp_ortu': '08123456789',
            'pekerjaan_ortu': 'swasta',
            'penghasilan_ortu': '3jt_5jt',
        }
        file_content = b'test content'
        file_data = {
            'file_pasfoto': SimpleUploadedFile("pasfoto.jpg", file_content, content_type="image/jpeg"),
            'file_ktp': SimpleUploadedFile("ktp.jpg", file_content, content_type="image/jpeg"),
            'file_kk': SimpleUploadedFile("kk.jpg", file_content, content_type="image/jpeg"),
            'file_ijazah': SimpleUploadedFile("ijazah.pdf", file_content, content_type="application/pdf"),
        }
        form = PendaftaranForm(data=data, files=file_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class DokumenUploadFormTest(TestCase):

    def test_valid_file_size(self):
        # Create a small valid file
        file_content = b'test content'
        test_file = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")
        
        data = {'jenis_dokumen': 'ktp'}
        file_data = {'file': test_file}
        
        form = DokumenUploadForm(data=data, files=file_data)
        self.assertTrue(form.is_valid())

    def test_file_too_large(self):
        # Create a file slightly larger than 2MB
        file_content = b'0' * (2 * 1024 * 1024 + 1024)
        test_file = SimpleUploadedFile("large.pdf", file_content, content_type="application/pdf")
        
        data = {'jenis_dokumen': 'ktp'}
        file_data = {'file': test_file}
        
        form = DokumenUploadForm(data=data, files=file_data)
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)
