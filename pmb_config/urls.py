"""
URL configuration for Sistem Informasi PMB.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pendaftaran.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Django Debug Toolbar
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

# Customize admin site
admin.site.site_header = 'PMB - Universitas Nusantara Jaya'
admin.site.site_title = 'Admin PMB UNJ'
admin.site.index_title = 'Panel Administrasi PMB'
