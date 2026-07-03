"""
Models untuk aplikasi accounts.

Mengelola profil pengguna yang memperluas model User bawaan Django
dengan field role untuk membedakan Calon Mahasiswa, Admin PMB, dan Super Admin.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Profil pengguna yang terhubung One-to-One dengan User Django.

    Attributes:
        user (User): Relasi one-to-one dengan model User bawaan Django.
        role (str): Peran pengguna dalam sistem (calon_mahasiswa, admin_pmb, super_admin).
        nik (str): Nomor Induk Kependudukan (16 digit), unik per pengguna.
        nisn (str): Nomor Induk Siswa Nasional (10 digit), unik per pengguna.
    """

    ROLE_CHOICES = [
        ('calon_mahasiswa', 'Calon Mahasiswa'),
        ('admin_pmb', 'Admin PMB'),
        ('super_admin', 'Super Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='calon_mahasiswa')
    nik = models.CharField(max_length=16, unique=True, blank=True, null=True, verbose_name='NIK')
    nisn = models.CharField(max_length=10, unique=True, blank=True, null=True, verbose_name='NISN')

    class Meta:
        verbose_name = 'Profil Pengguna'
        verbose_name_plural = 'Profil Pengguna'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        """Cek apakah user adalah Admin PMB atau Super Admin."""
        return self.role in ('admin_pmb', 'super_admin')

    @property
    def is_super_admin(self):
        """Cek apakah user adalah Super Admin."""
        return self.role == 'super_admin'


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Signal handler untuk otomatis membuat/update Profile saat User disimpan.

    Parameters:
        sender: Model class yang mengirim signal (User).
        instance: Instance User yang baru disimpan.
        created (bool): True jika User baru dibuat.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
