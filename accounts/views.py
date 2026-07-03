"""
Views untuk aplikasi accounts.

Menangani registrasi, login, logout, dan reset password.
Sesuai PRD FR-06 s.d. FR-10 dan TRD Bagian 7.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import RegistrationForm, LoginForm


def register_view(request):
    """
    View untuk registrasi akun calon mahasiswa baru.

    GET: Menampilkan form registrasi.
    POST: Memproses data registrasi, membuat User + Profile.

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Render halaman register atau redirect ke login.
    """
    if request.user.is_authenticated:
        return redirect('pendaftaran:status')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Buat User
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['nama_lengkap'].split(' ')[0],
                last_name=' '.join(form.cleaned_data['nama_lengkap'].split(' ')[1:]),
            )
            # Update Profile (auto-created via signal)
            user.profile.role = 'calon_mahasiswa'
            user.profile.save()

            messages.success(request, 'Akun berhasil dibuat! Silakan login.')
            return redirect('accounts:login')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    View untuk login pengguna.

    GET: Menampilkan form login.
    POST: Memproses kredensial (mendukung email atau username) dan membuat session.
    """
    if request.user.is_authenticated:
        return redirect('pendaftaran:status')

    if request.method == 'POST':
        username_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        print("--- DEBUG LOGIN ---")
        print(f"Username input: '{username_input}'")
        print(f"Password length: {len(password)}")

        # Cari user berdasarkan username ATAU email (lebih fleksibel dan aman)
        from django.db.models import Q
        user_obj = User.objects.filter(Q(username__iexact=username_input) | Q(email__iexact=username_input)).first()
        print(f"User found: {user_obj}")

        user = None
        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            print(f"Auth result: {user}")
        else:
            print("No user matched the input")

        if user is not None:
            login(request, user)
            messages.success(request, f'Selamat datang, {user.get_full_name() or user.username}!')

            # Redirect berdasarkan role
            if hasattr(user, 'profile') and user.profile.is_admin:
                return redirect('dashboard:home')
            return redirect('pendaftaran:status')
        else:
            messages.error(request, 'Email/Username atau password salah.')

    form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@require_POST
def logout_view(request):
    """
    View untuk logout pengguna.

    Parameters:
        request: HttpRequest object.

    Returns:
        HttpResponse: Redirect ke landing page.
    """
    logout(request)
    messages.info(request, 'Anda telah logout.')
    return redirect('pendaftaran:landing')
