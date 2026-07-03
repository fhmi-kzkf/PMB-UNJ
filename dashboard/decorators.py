"""
Decorators untuk aplikasi dashboard.

Berisi decorator akses kontrol untuk admin PMB.
Sesuai TRD Bagian 8 (Security: @login_required + @user_passes_test).
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """
    Decorator yang membatasi akses hanya untuk Admin PMB dan Super Admin.

    Menggabungkan @login_required dengan pengecekan role pada profile.

    Parameters:
        view_func: Function view yang akan dibungkus.

    Returns:
        function: Wrapped view function.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.is_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('pendaftaran:landing')
    return wrapper
