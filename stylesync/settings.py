# stylesync/settings.py

import os
from pathlib import Path

# This figures out the base directory of your project.
BASE_DIR = Path(__file__).resolve().parent.parent

# A secret key used for security purposes. Keep this safe in a real project!
SECRET_KEY = 'django-insecure-a-temporary-secret-key-for-development'

# DEBUG=True shows you detailed error pages. For a live website, this MUST be False.
DEBUG = True

# A list of domain names that this website is allowed to serve.
ALLOWED_HOSTS = []

# This is a list of all the "apps" that your project is using.
# We must add our new 'booking' app here.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Our new app that handles all booking logic
    'booking.apps.BookingConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# This tells Django where to find the main list of URLs for the project.
ROOT_URLCONF = 'stylesync.urls'

# This tells Django how and where to find your HTML files (Templates).
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # We will create a global 'templates' folder at the project root.
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'stylesync.wsgi.application'

# Database configuration. For learning, we use SQLite, which is a simple file.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- File Handling ---
# URL for serving static files like CSS and JavaScript.
STATIC_URL = 'static/'
# Where user-uploaded files (like staff photos) will be stored.
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# After a user logs in, they will be redirected to the homepage ('/').
LOGIN_REDIRECT_URL = '/'

# --- Custom App Settings ---
# For development, this makes Django print emails to the console instead of sending them.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@stylesync.com'

# Stripe API Keys (get these from your Stripe.com test dashboard)
STRIPE_PUBLISHABLE_KEY = 'pk_test_YOUR_PUBLISHABLE_KEY' # Replace with your key
STRIPE_SECRET_KEY = 'sk_test_YOUR_SECRET_KEY'     # Replace with your key
STRIPE_WEBHOOK_SECRET = 'whsec_...'             # Replace with your key from the Stripe CLI