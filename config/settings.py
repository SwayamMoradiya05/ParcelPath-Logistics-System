"""
Django settings for ParcelPath.

Project: ParcelPath
Framework: Django
Database: SQLite
"""

from pathlib import Path
import os

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


# -----------------------------------------------------------------------------
# Core Settings
# -----------------------------------------------------------------------------

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-local-development-key",
)

DEBUG = os.environ.get(
    "DEBUG",
    "True",
) == "True"

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost",
).split(",")


# -----------------------------------------------------------------------------
# Installed Applications
# -----------------------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

LOCAL_APPS = [
    "apps.accounts.apps.AccountsConfig",
    "apps.customers",
    "apps.drivers",
    "apps.shipments",
    "apps.tracking",
    "apps.routes",
    "apps.notifications",
    "apps.dashboard",
    "apps.contact",
    "apps.destinations",
    "apps.core",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS


# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# -----------------------------------------------------------------------------
# URL Configuration
# -----------------------------------------------------------------------------

ROOT_URLCONF = "config.urls"


# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.notifications.context_processors.notification_context",
                "apps.core.context_processors.global_settings",
                "apps.core.context_processors.notification_context",
            ],
        },
    },
]


# -----------------------------------------------------------------------------
# WSGI
# -----------------------------------------------------------------------------

WSGI_APPLICATION = "config.wsgi.application"


# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'database' / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# -----------------------------------------------------------------------------
# Password Validation
# -----------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]



# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# -----------------------------------------------------------------------------
# Static Files
# -----------------------------------------------------------------------------

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


# -----------------------------------------------------------------------------
# Media Files
# -----------------------------------------------------------------------------

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# -----------------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------------

LOGIN_URL = "accounts:login"

LOGIN_REDIRECT_URL = "dashboard:dashboard"

LOGOUT_REDIRECT_URL = "home"

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# -----------------------------------------------------------------------------
# Email
# -----------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = "ParcelPath <no-reply@parcelpath.com>"


# -----------------------------------------------------------------------------
# Session Settings
# -----------------------------------------------------------------------------

SESSION_COOKIE_AGE = 60 * 60 * 24

SESSION_SAVE_EVERY_REQUEST = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# -----------------------------------------------------------------------------
# Messages
# -----------------------------------------------------------------------------

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}


# -----------------------------------------------------------------------------
# Default Primary Key
# -----------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# -----------------------------------------------------------------------------
# File Upload Limits
# -----------------------------------------------------------------------------

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760


# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------

X_FRAME_OPTIONS = "DENY"

CSRF_COOKIE_HTTPONLY = False

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = False

SESSION_COOKIE_SECURE = False

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True


# -----------------------------------------------------------------------------
# Project Information
# -----------------------------------------------------------------------------

PROJECT_NAME = "ParcelPath"

PROJECT_VERSION = "1.0.0"

COMPANY_NAME = "ParcelPath Logistics"

SUPPORT_EMAIL = "support@parcelpath.com"

DEFAULT_COUNTRY = "India"


# -----------------------------------------------------------------------------
# Parcel Status
# -----------------------------------------------------------------------------

PARCEL_STATUS = [
    ("BOOKED", "Booked"),
    ("CONFIRMED", "Confirmed"),
    ("PICKUP_SCHEDULED", "Pickup Scheduled"),
    ("PICKED_UP", "Picked Up"),
    ("WAREHOUSE", "Warehouse"),
    ("SORTING_CENTER", "Sorting Center"),
    ("IN_TRANSIT", "In Transit"),
    ("DESTINATION_HUB", "Destination Hub"),
    ("OUT_FOR_DELIVERY", "Out For Delivery"),
    ("DELIVERED", "Delivered"),
    ("CANCELLED", "Cancelled"),
]


# -----------------------------------------------------------------------------
# User Roles
# -----------------------------------------------------------------------------

USER_ROLES = [
    ("ADMIN", "Administrator"),
    ("DISPATCHER", "Dispatcher"),
    ("DRIVER", "Driver"),
    ("CUSTOMER", "Customer"),
]


# -----------------------------------------------------------------------------
# Pagination
# -----------------------------------------------------------------------------

PAGE_SIZE = 10


# -----------------------------------------------------------------------------
# Date Formats
# -----------------------------------------------------------------------------

DATE_INPUT_FORMATS = [
    "%d-%m-%Y",
    "%Y-%m-%d",
]



DATETIME_FORMAT = "%d %b %Y %I:%M %p"


if not DEBUG:

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True

    SECURE_PROXY_SSL_HEADER = (
        ("HTTP_X_FORWARDED_PROTO", "https")
    )

