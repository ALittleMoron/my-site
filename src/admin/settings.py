import sys
from datetime import timedelta
from pathlib import Path
from typing import cast

from decouple import AutoConfig
from django.templatetags.static import static
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR.parent
PROJECT_ROOT_DIR = SRC_DIR.parent

sys.path.insert(0, BASE_DIR.as_posix())
config = AutoConfig((PROJECT_ROOT_DIR / ".env").as_posix())

SECRET_KEY = config("ADMIN_SECRET_KEY", default="secret")
DEBUG = config("ADMIN_DEBUG", default=True, cast=bool)
ALLOWED_HOSTS: list[str] = cast(
    list[str],
    config(
        "ADMIN_ALLOWED_HOST",
        default="*",
        cast=lambda hosts: hosts.split(","),
    ),
)
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = 'SAMEORIGIN'
INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS = [
    # pre-builtin third-parties
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    # builtin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'mdeditor',
    'django_minio_backend',
    'import_export',
    "debug_toolbar",
    # applications
    'core.apps.CoreConfig',
    'competency_matrix.apps.CompetencyMatrixConfig',
    # post-application third-partis
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
if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'admin.urls'

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

WSGI_APPLICATION = 'admin.wsgi.application'

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': config('DB_NAME', default='my_site_database'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    },
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MINIO_USE_HTTPS = config('MINIO_USE_HTTPS', default=False, cast=bool)
MINIO_ENDPOINT = config('MINIO_ENDPOINT', default='localhost:9000')
MINIO_ACCESS_KEY = config('MINIO_ACCESS_KEY', default='minioadmin')
MINIO_SECRET_KEY = config('MINIO_SECRET_KEY', default='minioadmin')
MINIO_URL_EXPIRY_HOURS = timedelta(days=1)
MINIO_POLICY_HOOKS: list[tuple[str, dict]] = []
MINIO_CONSISTENCY_CHECK_ON_START = True
MINIO_BUCKET_CHECK_ON_SAVE = True
MINIO_PUBLIC_BUCKETS: list[str] = ['media', 'admin-static']
MINIO_PRIVATE_BUCKETS: list[str] = []
MINIO_MEDIA_FILES_BUCKET = 'media'
MINIO_STATIC_FILES_BUCKET = 'admin-static'
DEFAULT_FILE_STORAGE = 'django_minio_backend.models.MinioBackend'
STATICFILES_STORAGE = 'django_minio_backend.models.MinioBackendStatic'
STORAGES = {
    'default': {'BACKEND': 'django_minio_backend.models.MinioBackend'},
    'staticfiles': {'BACKEND': 'django_minio_backend.models.MinioBackendStatic'},
}
# TODO: FIXME
STATIC_URL = 'http://localhost:9000/admin-static/'
MEDIA_URL = 'http://localhost:9000/media/'
STATICFILES_DIRS = [BASE_DIR / 'static/']

MARTOR_THEME = 'semantic'
MARTOR_ENABLE_CONFIGS = {
    'emoji': 'true',
    'imgur': 'true',
    'mention': 'false',
    'jquery': 'true',
    'living': 'false',
    'spellcheck': 'false',
    'hljs': 'true',
}
MARTOR_TOOLBAR_BUTTONS = [
    'bold',
    'italic',
    'horizontal',
    'heading',
    'pre-code',
    'blockquote',
    'unordered-list',
    'ordered-list',
    'link',
    'image-link',
    'image-upload',
    'emoji',
    'direct-mention',
    'toggle-maximize',
    'help',
]

MARTOR_ENABLE_LABEL = True
MARTOR_ENABLE_ADMIN_CSS = False
MARTOR_MARKDOWNIFY_TIMEOUT = 0
MARTOR_UPLOAD_PATH = 'martor'
MARTOR_UPLOAD_URL = '/markdown-upload-image/'
MAX_IMAGE_UPLOAD_SIZE = 10485760

MDEDITOR_CONFIGS = {
    'default': {
        'width': '90% ',
        'height': 500,
        'toolbar': [
            "undo",
            "redo",
            "|",
            "bold",
            "del",
            "italic",
            "quote",
            "ucwords",
            "uppercase",
            "lowercase",
            "|",
            "h1",
            "h2",
            "h3",
            "h5",
            "h6",
            "|",
            "list-ul",
            "list-ol",
            "hr",
            "|",
            "link",
            "reference-link",
            "image",
            "code",
            "preformatted-text",
            "code-block",
            "table",
            "datetime",
            "emoji",
            "html-entities",
            "pagebreak",
            "goto-line",
            "|",
            "preview",
            "watch",
            "fullscreen",
            "||",
            "help",
        ],  # custom edit box toolbar
        'upload_image_formats': [
            "jpg",
            "jpeg",
            "gif",
            "png",
            "bmp",
            "webp",
        ],  # image upload format type
        'upload_image_url': '/markdown-upload-image/',
        'theme': 'default',
        'preview_theme': 'default',
        'editor_theme': 'default',
        'toolbar_autofixed': True,
        'search_replace': True,
        'emoji': True,
        'tex': True,
        'flow_chart': True,
        'sequence': True,
        'watch': True,
        'lineWrapping': True,
        'lineNumbers': True,
        'language': 'ru',
    },
}

UNFOLD = {
    "SITE_TITLE": "Мой сайт",
    "SITE_HEADER": "Админ-панель",
    "THEME": "dark",
    "SITE_ICON": {
        "light": lambda _: static("core/icon-light.png"),  # light mode
        "dark": lambda _: static("core/icon-dark.png"),  # dark mode
    },
    "TABS": [
        {
            "models": ["competency_matrix.competencymatrixitem"],
            "items": [
                {
                    "title": "Элементы матрицы компетенций",
                    "icon": "sports_motorsports",
                    "link": reverse_lazy("admin:competency_matrix_competencymatrixitem_changelist"),
                },
                {
                    "title": "Заполненные",
                    "icon": "sports_motorsports",
                    "link": lambda _: '{url}?subsection__isnull=false&grade__isnull=false'.format(
                        url=reverse_lazy("admin:competency_matrix_competencymatrixitem_changelist"),
                    ),
                },
                {
                    "title": "Опубликованные",
                    "icon": "sports_motorsports",
                    "link": lambda _: '{url}?status__exact=published'.format(
                        url=reverse_lazy("admin:competency_matrix_competencymatrixitem_changelist"),
                    ),
                },
                {
                    "title": "Черновики",
                    "icon": "sports_motorsports",
                    "link": lambda _: '{url}?status__exact=draft'.format(
                        url=reverse_lazy("admin:competency_matrix_competencymatrixitem_changelist"),
                    ),
                },
            ],
        },
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                'title': 'Навигация',
                'items': [
                    {
                        "title": "Панель",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": "Матрица компетенций",
                        "icon": "school",
                        "link": reverse_lazy(
                            "admin:competency_matrix_competencymatrixitem_changelist",
                        ),
                    },
                ],
            },
            {
                "title": "Пользователи и группы",
                "collapsible": True,
                "items": [
                    {
                        "title": "Пользователи",
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": "Группы",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "75 85 99",
            "default-dark": "209 213 219",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "104 217 17",  # accent colors for text
            "600": "80 171 10",  # background of main color (buttons, icons)
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
}
