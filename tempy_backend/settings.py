from pathlib import Path
from decouple import config  # for .env support
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Secret Key (from .env)
SECRET_KEY = config("DJANGO_SECRET_KEY", default="unsafe-secret-key")

# ⚙️ Debug / Hosts
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = [
    host.strip()
    for host in config("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")
    if host.strip()
]

# 📦 Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',

    # Your apps
    'auth_app',
    # 'eventform_app',
    # 'resume_app',
    # 'biodata_app',
    # 'invitation_app',
    # 'certificate_app',
    # 'visiting_card_app',
    # 'funeral_app',
    # 'businessdoc_app',
    # 'socialcontent_app',
    # 'greeting_app',
    # 'storages',
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

ROOT_URLCONF = 'tempy_backend.urls'

# ✅ Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'tempy_backend' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tempy_backend.wsgi.application'

# 🌍 Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# 📂 Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 📂 Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ REST Framework defaults (JWT + permissions)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# ✅ SimpleJWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ✅ PostgreSQL Database settings
DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'tempy_backend_db',
#         'USER': 'postgres',
#         'PASSWORD': 'postgres',
#         # 'ENGINE': 'django.db.backends.postgresql',
#         # 'NAME': config("POSTGRES_DB", default="postgres"),
#         # 'USER': config("POSTGRES_USER", default="postgres"),
#         # 'PASSWORD': config("POSTGRES_PASSWORD", default="postgres"),
#         #'HOST': config("POSTGRES_HOST", default="localhost"),
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#         #'PORT': config("POSTGRES_PORT", default="5432"),
#     }
# }

# ✅ Custom User Model
AUTH_USER_MODEL = "auth_app.User"

# ✅ Email / SMTP settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='testtempy56@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')  # Gmail App Password required
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=f"Tempy <{EMAIL_HOST_USER}>")

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }
# # ================= AWS S3 CONFIG =================

# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# AWS_ACCESS_KEY_ID = "YOUR_KEY"
# AWS_SECRET_ACCESS_KEY = "YOUR_SECRET"
# AWS_STORAGE_BUCKET_NAME = "your-bucket-name"
# AWS_S3_REGION_NAME = "ap-south-1"

# AWS_QUERYSTRING_AUTH = False
# AWS_S3_FILE_OVERWRITE = False
# AWS_DEFAULT_ACL = None

# AWS_S3_SIGNATURE_VERSION = "s3v4"


# MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"


