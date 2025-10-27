"""
WSGI config for surveillance_core project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'surveillance_core.settings')

application = get_wsgi_application()