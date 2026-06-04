# Production-Grade Settings for Railway + Neon + Cloudflare R2
# This replaces the old Render-based settings with Railway, Neon, and R2 integration

import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'apps'))

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

# Secret key from environment - MUST be set in production
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', None)
if not SECRET_KEY:
    if os.getenv('DJANGO_DEBUG') == 'True':
        SECRET_KEY = 'dev-insecure-key-only-for-local-development'
    else:
        raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set in production')

# Debug mode - should be False in production
DEBUG = os.getenv('DJANGO_DEBUG', 'False').strip().lower() in ('true', '1', 'yes')

# Allowed hosts configuration
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1').split()
# Railway automatically sets RAILWAY_DOMAIN_URL when deployed
railway_domain = os.getenv('RAILWAY_DOMAIN_URL', '').strip()
if railway_domain and railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(railway_domain)

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

INSTALLED_APPS = [
    # Django built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.postgres',  # PostgreSQL-specific features
    
    # Third-party packages
    'rest_framework',
    'django_filters',
    'corsheaders',
    'ckeditor',
    'ckeditor_uploader',
    'axes',  # Brute force protection
    'django_celery_beat',  # Celery beat scheduler
    'django_celery_results',  # Celery results backend
    
    # Project apps
    'accounts',
    'blog',
    'newsletter',
    'analytics',
    'ads',
]

SITE_ID = 1

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

MIDDLEWARE = [
    # Security middleware
    'django.middleware.security.SecurityMiddleware',
    
    # Whitenoise for static file serving
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # CORS middleware (if API is needed)
    'corsheaders.middleware.CorsMiddleware',
    
    # Standard Django middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom security middleware
    'axes.middleware.AxesMiddleware',  # Brute force protection
]

# ============================================================================
# TEMPLATE CONFIGURATION
# ============================================================================

ROOT_URLCONF = 'techsphere.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

WSGI_APPLICATION = 'techsphere.wsgi.application'
ASGI_APPLICATION = 'techsphere.asgi.application'

# ============================================================================
# DATABASE CONFIGURATION (NEON POSTGRESQL)
# ============================================================================

def get_database_config():
    """
    Configure database connection.
    Supports multiple environment variable formats:
    - DATABASE_URL (standard format from Railway)
    - Individual env vars: PGHOST, PGDATABASE, PGUSER, PGPASSWORD, PGPORT
    """
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        parsed_db_url = urlparse(database_url)
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed_db_url.path.lstrip('/'),
            'USER': parsed_db_url.username,
            'PASSWORD': parsed_db_url.password,
            'HOST': parsed_db_url.hostname,
            'PORT': parsed_db_url.port or '5432',
            'CONN_MAX_AGE': 600,  # Connection pooling
            'OPTIONS': {
                'connect_timeout': 10,
                'options': '-c default_transaction_isolation=read_committed',
            },
        }
    
    # Fallback to individual environment variables
    if os.getenv('PGHOST'):
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('PGDATABASE', 'techsphere'),
            'USER': os.getenv('PGUSER', 'techsphere_user'),
            'PASSWORD': os.getenv('PGPASSWORD', ''),
            'HOST': os.getenv('PGHOST'),
            'PORT': os.getenv('PGPORT', '5432'),
            'CONN_MAX_AGE': 600,
            'OPTIONS': {
                'connect_timeout': 10,
                'options': '-c default_transaction_isolation=read_committed',
            },
        }
    
    # Local development with Docker Compose
    if DEBUG:
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'techsphere'),
            'USER': os.getenv('POSTGRES_USER', 'techsphere_user'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'password'),
            'HOST': os.getenv('POSTGRES_HOST', 'db'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
    
    # Fallback for build-time operations (collectstatic, etc.)
    if 'collectstatic' in sys.argv or 'migrate' in sys.argv:
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    
    raise ImproperlyConfigured(
        'Database configuration is missing. '
        'Set DATABASE_URL or PGHOST in environment variables.'
    )

DATABASES = {
    'default': get_database_config()
}

# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================================================
# LOCALIZATION
# ============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ============================================================================
# STATIC FILES CONFIGURATION (With Whitenoise + Cloudflare CDN)
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Whitenoise for efficient static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Whitenoise caching settings
WHITENOISE_IMMUTABLE_FILE_TEST = lambda path, url: 'static' in path and '.' in url

# Cache static files for 1 year (safe due to content hashing)
WHITENOISE_MAX_AGE = 31536000

# ============================================================================
# MEDIA FILES CONFIGURATION (Cloudflare R2)
# ============================================================================

# Media files via Cloudflare R2 (S3-compatible)
USE_R2 = os.getenv('USE_R2', 'False').strip().lower() in ('true', '1', 'yes')

if USE_R2:
    # Cloudflare R2 Configuration
    AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'techsphere-media')
    AWS_S3_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL', '')
    AWS_S3_CUSTOM_DOMAIN = os.getenv('R2_CUSTOM_DOMAIN', '')
    
    # S3 Configuration
    AWS_S3_REGION_NAME = 'auto'  # Cloudflare R2 uses 'auto'
    AWS_S3_USE_SSL = True
    AWS_S3_VERIFY = True
    
    # File uploads
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=2592000',  # 30 days
    }
    
    # Use R2 for media storage
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'{AWS_S3_CUSTOM_DOMAIN}/media/' if AWS_S3_CUSTOM_DOMAIN else f'{AWS_S3_ENDPOINT_URL}/media/'
    
    # django-storages for S3/R2
    INSTALLED_APPS.append('storages')
else:
    # Local file storage (development)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# DJANGO ADMIN CUSTOMIZATION
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'
LOGIN_REDIRECT_URL = reverse_lazy('blog:home')
LOGOUT_REDIRECT_URL = reverse_lazy('blog:home')

# ============================================================================
# CKEDITOR CONFIGURATION
# ============================================================================

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 400,
        'width': '100%',
        'extraAllowedContent': 'iframe[*]{*}(*)',
    }
}

# ============================================================================
# DJANGO REST FRAMEWORK
# ============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# CELERY & REDIS CONFIGURATION
# ============================================================================

# Redis URL from Railway or local Docker
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'send-pending-newsletters': {
        'task': 'newsletter.tasks.send_pending_newsletters',
        'schedule': 60.0,  # Every minute
    },
    'update-post-analytics': {
        'task': 'analytics.tasks.update_post_analytics',
        'schedule': 300.0,  # Every 5 minutes
    },
    'aggregate-daily-stats': {
        'task': 'analytics.tasks.aggregate_daily_stats',
        'schedule': 3600.0,  # Every hour
    },
}

# ============================================================================
# CACHE CONFIGURATION (Redis)
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# Axes - Brute force protection
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 hour
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_USE_USER_AGENT = True

# HTTPS/SSL Configuration
SECURE_SSL_REDIRECT = not DEBUG and os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
SESSION_COOKIE_SECURE = not DEBUG and os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_SECURE = not DEBUG and os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy (CSP)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", 'cdn.ckeditor.com', '*.google-analytics.com', '*.googletagmanager.com')
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", 'cdn.jsdelivr.net', 'fonts.googleapis.com')
CSP_FONT_SRC = ("'self'", 'fonts.gstatic.com', 'cdn.jsdelivr.net')
CSP_IMG_SRC = ("'self'", 'data:', 'https:')
CSP_MEDIA_SRC = ("'self'", 'https:')
CSP_FRAME_SRC = ("'self'", 'www.youtube.com', 'player.vimeo.com')

# Allowed hosts for inline styles/scripts (for CKEditor)
ALLOWED_HOSTS_WITH_SUBDOMAINS = os.getenv('ALLOWED_HOSTS_WITH_SUBDOMAINS', '').split(',') if os.getenv('ALLOWED_HOSTS_WITH_SUBDOMAINS') else []

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'

# SMTP Configuration (for production)
if not DEBUG:
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@techsphere.dev')
else:
    DEFAULT_FROM_EMAIL = 'noreply@techsphere.local'

# ============================================================================
# GOOGLE ANALYTICS & ADSENSE
# ============================================================================

GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID', '')
GOOGLE_ADSENSE_CLIENT_ID = os.getenv('GOOGLE_ADSENSE_CLIENT_ID', '')
GOOGLE_ADSENSE_SLOT_ID = os.getenv('GOOGLE_ADSENSE_SLOT_ID', '')

# ============================================================================
# SENTRY ERROR TRACKING
# ============================================================================

SENTRY_ENABLED = os.getenv('SENTRY_ENABLED', 'False') == 'True'
if SENTRY_ENABLED:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.getenv('SENTRY_TRACE_RATE', '0.1')),
        send_default_pii=False,
        environment=os.getenv('ENVIRONMENT', 'production'),
    )

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# PAGINATION
# ============================================================================

PAGINATION_SIZE = int(os.getenv('PAGINATION_SIZE', '10'))

# ============================================================================
# SITE CONFIGURATION
# ============================================================================

SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')
SITE_NAME = os.getenv('SITE_NAME', 'TechSphere')

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURES = {
    'NEWSLETTER': True,
    'COMMENTS': True,
    'AFFILIATE_MARKETING': True,
    'ADSENSE': True,
    'SPONSORED_CONTENT': True,
    'USER_RATINGS': True,
    'READING_HISTORY': True,
}
