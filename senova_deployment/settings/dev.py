from .base import *

# Security
DEBUG = True
ALLOWED_HOSTS = ['*']


# FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
# DOMAIN = os.getenv('DOMAIN', 'localhost:5173')
# SITE_NAME = 'Senova Store'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_ROOT = BASE_DIR / 'media'

# Development-specific settings
CORS_ALLOW_ALL_ORIGINS = True

# Email - use console backend for development
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

