from .settings import *

# Production settings
DEBUG = False

# Allow your Back4App domain
ALLOWED_HOSTS = [
    'africadiseasesurveillance-6gvw2n7s.b4a.run',
    'localhost',
    '127.0.0.1',
]

# Security settings
CSRF_TRUSTED_ORIGINS = [
    'https://africadiseasesurveillance-6gvw2n7s.b4a.run',
]

# Parse configuration - use environment variables in production
import os
PARSE_APP_ID = os.getenv('PARSE_APP_ID', 'K6lQVSqx3B7BU5ePJ1SvdhtXQN7h8S9OMEdOOuNj')
PARSE_REST_API_KEY = os.getenv('PARSE_REST_API_KEY', 'cLxvBXdulLXGklKbBi9Lbhj6Q07CXvVDskWFTZ8K')
PARSE_MASTER_KEY = os.getenv('PARSE_MASTER_KEY', 'c7RPaycZmbjf5TBi8vKCKZ29iNnaTkHaGqiulRyf')

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')