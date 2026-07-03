"""
WSGI config for Sistem Informasi PMB.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pmb_config.settings')

application = get_wsgi_application()
