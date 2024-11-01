from datetime import timedelta
import os
from pathlib import Path

# import datetime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "qv*o1&&x%#jtsn)5((g+yw#%3_a$ykfof6b-)j^i$1a8se*7c8"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.getenv("DEBUG_SERVER", 0)) == 1

ALLOWED_HOSTS = []
CORS_ALLOWED_ORIGINS = []

if os.getenv("ALLOWED_HOSTS"):
    ALLOWED_HOSTS += os.getenv("ALLOWED_HOSTS").split(",")
    CORS_ALLOWED_ORIGINS += os.getenv("ALLOWED_HOSTS").split(",")

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "daphne",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "django.contrib.sites",
    "corsheaders",
    "channels",
    "api",
    "core",
    "users",
    "user_course"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if not DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "assistant_db"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
            "HOST": os.getenv("DB_HOST", "postgres"),  # Default to localhost if not set
            "PORT": os.getenv("DB_PORT", "5432"),  # Default to 5432 if not set
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"

AUTH_USER_MODEL = "users.CustomUser"

SITE_ID = 1

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if DEBUG:
    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(days=5),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
    }

# AI Settings
MAX_FOLLOW_UP_LIMIT=int(os.getenv("max_follow_up_questions", 3))
TOP_K=5
MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
DATABASE=os.getenv('database')
PINECONE_API_KEY=os.getenv('pinecone_api_key')
PINECONE_INDEX_NAME="textbook-chunks"
CHUNKS_FILE="text_chunks.json"


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}