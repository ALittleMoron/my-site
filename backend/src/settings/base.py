from settings.config import config

BASE_DIR = config.dir.src_path
PROJECT_ROOT_DIR = config.dir.root_path

SECRET_KEY = config.app.secret_key.get_secret_value()
DEBUG = config.app.debug
ALLOWED_HOSTS = config.app.allowed_hosts
CSRF_COOKIE_HTTPONLY = config.csrf.cookie_httponly
CSRF_TRUSTED_ORIGINS = config.csrf.trusted_origins
X_FRAME_OPTIONS = config.app.x_frame_options
INTERNAL_IPS = config.app.internal_ips

INSTALLED_APPS = [
    # pre-builtin third-party
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    # builtin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "ninja",
    "ninja_extra",
    "mdeditor",
    "django_minio_backend",
    "import_export",
    "debug_toolbar",
    "anydi.ext.django",
    # applications
    "infra.apps.DjangoInfraConfig",
    "db.apps.DjangoDatabaseConfig",
]
MIDDLEWARE = [
    "anydi.ext.django.middleware.request_scoped_middleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [config.dir.src_path / "templates"],
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

WSGI_APPLICATION = "wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config.database.name,
        "USER": config.database.user,
        "PASSWORD": config.database.password.get_secret_value(),
        "HOST": config.database.host,
        "PORT": config.database.port,
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = config.app.language_code
TIME_ZONE = config.app.time_zone
USE_I18N = config.app.use_i18n
USE_TZ = config.app.use_tz

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
