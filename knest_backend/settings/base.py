"""
Django settings for knest_backend project.
"""

from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-6ey*l+h+hyf0vnpu2)b*0(a2!f5*wy(_iva+7+18y^8!l$l4_$"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.151.37', '127.0.0.1', 'localhost']

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "channels",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rest_framework_simplejwt",
    "drf_yasg",  # Swagger/OpenAPI
    "django_filters",  # フィルタリング
    "knest_backend.apps.users.apps.UsersConfig",
    "knest_backend.apps.interests.apps.InterestsConfig",
    "knest_backend.apps.circles.apps.CirclesConfig",
    "knest_backend.apps.ai_support.apps.AISupportConfig",
    "knest_backend.apps.subscriptions.apps.SubscriptionsConfig",
    "knest_backend.apps.reactions.apps.ReactionsConfig",
    "knest_backend.apps.chat_messages.apps.ChatMessagesConfig",
    "knest_backend.apps.recommendations.apps.RecommendationsConfig",  # 推薦システム
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "knest_backend.urls"

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

WSGI_APPLICATION = "knest_backend.wsgi.application"

# Channels
ASGI_APPLICATION = "knest_backend.asgi.application"

# Channels Layers
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
        # "BACKEND": "channels_redis.core.RedisChannelLayer",
        # "CONFIG": {
        #     "hosts": [("127.0.0.1", 6379)],
        # },
    },
}

# CORS設定
CORS_ALLOW_ALL_ORIGINS = True  # 開発環境のみ
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# WebSocket URL
WEBSOCKET_URL = "/ws/"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ja"

TIME_ZONE = "Asia/Tokyo"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework設定
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# カスタムユーザーモデルの設定
AUTH_USER_MODEL = 'users.User'

# キャッシュの設定
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        # "BACKEND": "django_redis.cache.RedisCache",
        # "LOCATION": "redis://127.0.0.1:6379/1",
        # "OPTIONS": {
        #     "CLIENT_CLASS": "django_redis.client.DefaultClient",
        #     "SOCKET_CONNECT_TIMEOUT": 5,
        #     "SOCKET_TIMEOUT": 5,
        #     "RETRY_ON_TIMEOUT": True,
        #     "MAX_CONNECTIONS": 1000,
        #     "CONNECTION_POOL_KWARGS": {"max_connections": 100},
        # }
    }
}

# キャッシュのタイムアウト設定（秒）
CHAT_MESSAGE_CACHE_TIMEOUT = 60 * 5  # 5分
CHAT_UNREAD_COUNT_CACHE_TIMEOUT = 60  # 1分

# Logging configuration - シンプル版
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',  # DEBUGからWARNINGに変更
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',  # DEBUGからINFOに変更
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',  # DEBUGからWARNINGに変更
            'propagate': False,
        },
        'django.db.backends': {  # SQLクエリログを非表示
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'knest_backend.apps.users.views': {
            'handlers': ['console'],
            'level': 'INFO',  # DEBUGからINFOに変更
            'propagate': False,
        },
        'knest_backend.apps.recommendations': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Simple JWT設定
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# 次世代推薦システム設定
USE_NEW_RECOMMENDATION_ENGINE = True  # 新推薦エンジンを有効化
RECOMMENDATION_ENGINE_CONFIG = {
    'CACHE_TIMEOUT': 3600,  # 1時間
    'SIMILARITY_CACHE_TIMEOUT': 1800,  # 30分
    'MAX_SIMILAR_USERS': 50,
    'MIN_SIMILARITY_THRESHOLD': 0.3,
    'DEFAULT_DIVERSITY_FACTOR': 0.3,
    'ENABLE_BEHAVIORAL_TRACKING': True,
    'ENABLE_LEARNING': True,
} 