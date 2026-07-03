"""
Forms untuk aplikasi accounts.

Berisi form registrasi akun baru dan login untuk calon mahasiswa.
Sesuai PRD FR-06 s.d. FR-10.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class RegistrationForm(forms.Form):
    """
    Form registrasi akun calon mahasiswa baru.

    Melakukan validasi:
    - Keunikan NIK, NISN, dan email (FR-07).
    - Format NIK (16 digit) dan NISN (10 digit).
    - Password minimal 8 karakter.

    Fields:
        nama_lengkap (str): Nama lengkap pendaftar.
        email (str): Email aktif sebagai username login.
        nik (str): Nomor Induk Kependudukan.
        nisn (str): Nomor Induk Siswa Nasional.
        password (str): Password akun.
        password_confirm (str): Konfirmasi password.
    """

    nama_lengkap = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Masukkan nama lengkap',
            'id': 'id_nama_lengkap',
        }),
        label='Nama Lengkap'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'contoh@email.com',
            'id': 'id_email',
        }),
        label='Email'
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Minimal 8 karakter',
            'id': 'id_password',
        }),
        label='Password'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ulangi password',
            'id': 'id_password_confirm',
        }),
        label='Konfirmasi Password'
    )

    def clean_email(self):
        """Validasi keunikan email."""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email sudah terdaftar.')
        return email

    def clean(self):
        """Validasi password match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Password dan konfirmasi tidak cocok.')
        return cleaned_data


class LoginForm(AuthenticationForm):
    """
    Form login dengan styling custom.

    Menggunakan email sebagai username field.
    """

    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email',
            'id': 'id_login_email',
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'id': 'id_login_password',
        }),
        label='Password'
    )
