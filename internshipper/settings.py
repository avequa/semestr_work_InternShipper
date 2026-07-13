from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()  # читаем .env один раз

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-2g2h%om01kup-0n4hm%yc_h5h3mcg13n08_%^lpg4#jtak5iwh',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# В Docker фронт обращается по имени хоста контейнера — берём из env.
# Локально пусто => Django сам разрешает localhost при DEBUG=True.
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    # daphne ОБЯЗАТЕЛЬНО первым — иначе runserver поднимет старый WSGI-сервер,
    # который не понимает WebSocket.
    'daphne',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # ASGI / WebSocket
    'channels',

    'accounts.apps.AccountsConfig',
    'students',
    'partners',
    'teams',
    'projects',
    # 'feedbacks',
    'api',
    'chat',

    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',

    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',

    'dj_rest_auth',
    'dj_rest_auth.registration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'internshipper.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Обычный путь (WSGI) оставляем — gunicorn/runserver им пользуются.
WSGI_APPLICATION = 'internshipper.wsgi.application'
# Точка входа для ASGI (WebSocket). Файл создадим на следующем шаге.
ASGI_APPLICATION = 'internshipper.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'oris2sem_semestrovka1'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'admin'),
        # Локально 'localhost', в Docker — имя сервиса БД (например 'db').
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        # Локально твой порт 4444; в Docker внутри сети обычно 5432.
        'PORT': os.environ.get('POSTGRES_PORT', '4444'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 465))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'True') == 'True'
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SITE_ID = 1

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'InternShipper API',
    'DESCRIPTION': 'for oris checkpoint 2',
    'VERSION': '67',
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_ADAPTER = 'accounts.adapters.MySocialAccountAdapter'
LOGIN_REDIRECT_URL = '/'

# --------------------------------------------------------------------------
# КЭШ И СЕССИИ
# Раньше сессии хранились в Redis-кэше (SESSION_ENGINE = ...backends.cache).
# Когда Redis-контейнера не стало, кэш падал, а вместе с ним и сессии — и
# логин/allauth ломались. Теперь:
#   - кэш локальный (in-memory), не зависит от внешних сервисов;
#   - сессии в БД (дефолт Django) — надёжно и переживают перезапуск контейнера.
# --------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# SESSION_ENGINE по умолчанию = 'django.contrib.sessions.backends.db'
# (явно не указываем — это и есть хранение в Postgres).

# --------------------------------------------------------------------------
# DJANGO CHANNELS (WebSocket)
# Redis используется ТОЛЬКО как транспорт между подключениями (channel layer),
# а не как хранилище данных. История чата лежит в Postgres (модель chat.Message).
# Если Redis недоступен (например, ещё не подняли контейнер) — падаем на
# in-memory слой, чтобы dev-сервер всё равно стартовал.
# --------------------------------------------------------------------------
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
USE_REDIS_CHANNEL_LAYER = os.environ.get('USE_REDIS_CHANNEL_LAYER', 'True') == 'True'

if USE_REDIS_CHANNEL_LAYER:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [(REDIS_HOST, REDIS_PORT)],
            },
        }
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }

SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'APPS': [
            {
                'client_id': os.environ.get('GITHUB_CLIENT_ID', ''),
                'secret': os.environ.get('GITHUB_SECRET', ''),
                'key': '',
            },
        ],
        'SCOPE': ['user:email'],
    },
    'google': {
        'APPS': [
            {
                'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
                'secret': os.environ.get('GOOGLE_SECRET', ''),
                'key': '',
            },
        ],
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
}