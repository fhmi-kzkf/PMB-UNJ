"""
Forms untuk aplikasi pendaftaran.

Berisi form pendaftaran mahasiswa baru dan upload dokumen.
Sesuai PRD FR-11 s.d. FR-14.
"""

from django import forms
from .models import Pendaftar, Dokumen, Jurusan, JalurMasuk


class PendaftaranForm(forms.ModelForm):
    """
    Form pendaftaran mahasiswa baru komprehensif (5 Tahap).
    """
    # Tahap 5: File Uploads terintegrasi
    file_pasfoto = forms.FileField(
        label='Pasfoto Resmi (Latar Merah/Biru)',
        widget=forms.ClearableFileInput(attrs={'accept': '.jpg,.jpeg,.png', 'class': 'form-input form-file', 'id': 'id_file_pasfoto'}),
        help_text='Format JPG/PNG, Maksimal 2MB.'
    )
    file_ktp = forms.FileField(
        label='Scan KTP / Kartu Identitas',
        widget=forms.ClearableFileInput(attrs={'accept': '.jpg,.jpeg,.png,.pdf', 'class': 'form-input form-file', 'id': 'id_file_ktp'}),
        help_text='Format JPG/PDF, Maksimal 2MB.'
    )
    file_kk = forms.FileField(
        label='Scan Kartu Keluarga (KK)',
        widget=forms.ClearableFileInput(attrs={'accept': '.jpg,.jpeg,.png,.pdf', 'class': 'form-input form-file', 'id': 'id_file_kk'}),
        help_text='Format JPG/PDF, Maksimal 2MB.'
    )
    file_ijazah = forms.FileField(
        label='Scan Ijazah / Rapor / SKL',
        widget=forms.ClearableFileInput(attrs={'accept': '.jpg,.jpeg,.png,.pdf', 'class': 'form-input form-file', 'id': 'id_file_ijazah'}),
        help_text='Format JPG/PDF, Maksimal 2MB.'
    )
    file_sertifikat = forms.FileField(
        label='Scan Sertifikat Prestasi (Opsional)',
        widget=forms.ClearableFileInput(attrs={'accept': '.jpg,.jpeg,.png,.pdf', 'class': 'form-input form-file', 'id': 'id_file_sertifikat'}),
        required=False,
        help_text='Wajib untuk jalur prestasi. Format JPG/PDF, Maksimal 2MB.'
    )

    class Meta:
        model = Pendaftar
        fields = [
            # Tahap 1: Data Pribadi & Identitas
            'nama_lengkap', 'nik', 'nisn', 'tempat_lahir', 'tanggal_lahir', 'alamat', 'no_hp', 'email',
            # Tahap 2: Akademik
            'asal_sekolah', 'jurusan_sekolah', 'tahun_lulus', 'nilai_akademik',
            # Tahap 3: Pilihan Prodi
            'jurusan_pilihan1', 'jurusan_pilihan2', 'jalur_masuk', 'jenis_kelas',
            # Tahap 4: Orang Tua / Wali
            'nama_ayah', 'nama_ibu', 'no_hp_ortu', 'no_hp_ortu_cadangan', 'pekerjaan_ortu', 'penghasilan_ortu',
        ]
        widgets = {
            # Tahap 1
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama Lengkap sesuai Ijazah'}),
            'nik': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '16 digit NIK', 'pattern': '[0-9]{16}'}),
            'nisn': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '10 digit NISN', 'pattern': '[0-9]{10}'}),
            'tempat_lahir': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Kota/Kabupaten'}),
            'tanggal_lahir': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'alamat': forms.Textarea(attrs={'class': 'form-input form-textarea', 'rows': 3, 'placeholder': 'Alamat Lengkap'}),
            'no_hp': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Format WA: 08xxxxxxxxxx'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'contoh@email.com'}),

            # Tahap 2
            'asal_sekolah': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama Sekolah'}),
            'jurusan_sekolah': forms.Select(attrs={'class': 'form-input form-select'}),
            'tahun_lulus': forms.Select(choices=[(y, y) for y in range(2020, 2027)], attrs={'class': 'form-input form-select'}),
            'nilai_akademik': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0 - 100', 'min': 0, 'max': 100, 'step': '0.01'}),

            # Tahap 3
            'jurusan_pilihan1': forms.Select(attrs={'class': 'form-input form-select'}),
            'jurusan_pilihan2': forms.Select(attrs={'class': 'form-input form-select'}),
            'jalur_masuk': forms.Select(attrs={'class': 'form-input form-select'}),
            'jenis_kelas': forms.Select(attrs={'class': 'form-input form-select'}),

            # Tahap 4
            'nama_ayah': forms.TextInput(attrs={'class': 'form-input', 'placeholder': "Nama Ayah (Ketik '-' atau 'Almarhum' jika wafat)"}),
            'nama_ibu': forms.TextInput(attrs={'class': 'form-input', 'placeholder': "Nama Ibu (Ketik '-' atau 'Almarhum' jika wafat)"}),
            'no_hp_ortu': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '08xxxxxxxxxx (Utama)'}),
            'no_hp_ortu_cadangan': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '08xxxxxxxxxx (Opsional)'}),
            'pekerjaan_ortu': forms.Select(attrs={'class': 'form-input form-select'}),
            'penghasilan_ortu': forms.Select(attrs={'class': 'form-input form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['jurusan_pilihan1'].empty_label = "--- Pilih Program Studi 1 ---"
        self.fields['jurusan_pilihan2'].empty_label = "--- Pilih Program Studi 2 (Opsional) ---"
        self.fields['jalur_masuk'].empty_label = "--- Pilih Jalur Masuk ---"
        # Fix jurusan_sekolah to not slice off the first default option (IPA)
        self.fields['jurusan_sekolah'].choices = [("", "--- Pilih Jurusan Sekolah ---")] + list(self.fields['jurusan_sekolah'].choices)
        self.fields['pekerjaan_ortu'].choices = [("", "--- Pilih Pekerjaan Orang Tua ---")] + list(self.fields['pekerjaan_ortu'].choices)[1:]
        self.fields['penghasilan_ortu'].choices = [("", "--- Pilih Penghasilan Orang Tua ---")] + list(self.fields['penghasilan_ortu'].choices)[1:]

    def clean_file(self, field_name):
        file = self.cleaned_data.get(field_name)
        if file:
            max_size = 2 * 1024 * 1024  # 2MB
            if file.size > max_size:
                raise forms.ValidationError(
                    f'Ukuran file terlalu besar ({file.size // (1024 * 1024)}MB). Maksimal 2MB.'
                )
        return file

    def clean_file_pasfoto(self):
        return self.clean_file('file_pasfoto')

    def clean_file_ktp(self):
        return self.clean_file('file_ktp')

    def clean_file_kk(self):
        return self.clean_file('file_kk')

    def clean_file_ijazah(self):
        return self.clean_file('file_ijazah')

    def clean_file_sertifikat(self):
        return self.clean_file('file_sertifikat')

    def clean(self):
        """Validasi pilihan jurusan tidak boleh sama dan data orang tua."""
        cleaned_data = super().clean()
        pilihan1 = cleaned_data.get('jurusan_pilihan1')
        pilihan2 = cleaned_data.get('jurusan_pilihan2')
        if pilihan1 and pilihan2 and pilihan1 == pilihan2:
            raise forms.ValidationError(
                'Jurusan pilihan 1 dan pilihan 2 tidak boleh sama.'
            )
            
        # Validasi Orang Tua
        nama_ayah = cleaned_data.get('nama_ayah')
        nama_ibu = cleaned_data.get('nama_ibu')
        if not nama_ayah and not nama_ibu:
            raise forms.ValidationError(
                'Mohon isi minimal salah satu nama orang tua (Ayah atau Ibu). Jika sudah tiada, bisa diisi "Almarhum/Almarhumah" atau tanda strip (-).'
            )
            
        return cleaned_data


class DokumenUploadForm(forms.ModelForm):
    """
    Form untuk mengunggah dokumen pendaftar.

    Validasi:
    - Tipe file: PDF, JPG, JPEG, PNG.
    - Ukuran file: Maksimal 2MB.

    Sesuai PRD FR-14 dan TRD Bagian 8 (Security: upload file berbahaya).
    """

    class Meta:
        model = Dokumen
        fields = ['jenis_dokumen', 'file']
        widgets = {
            'jenis_dokumen': forms.Select(attrs={
                'class': 'form-input form-select',
                'id': 'id_jenis_dokumen',
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-input form-file',
                'id': 'id_file_dokumen',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
        }

    def clean_file(self):
        """Validasi ukuran file maksimal 2MB."""
        file = self.cleaned_data.get('file')
        if file:
            max_size = 2 * 1024 * 1024  # 2MB
            if file.size > max_size:
                raise forms.ValidationError(
                    f'Ukuran file terlalu besar ({file.size // 1024 // 1024}MB). '
                    f'Maksimal 2MB.'
                )
        return file
