from django.templatetags.static import static
from django.urls import reverse_lazy

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
            "models": ["db.competencymatrixitemmodel"],
            "items": [
                {
                    "title": "Элементы матрицы компетенций",
                    "link": reverse_lazy("admin:db_competencymatrixitemmodel_changelist"),
                },
                {
                    "title": "Опубликованные",
                    "link": lambda _: "{url}?status__exact=published".format(
                        url=reverse_lazy("admin:db_competencymatrixitemmodel_changelist"),
                    ),
                },
                {
                    "title": "Черновики",
                    "link": lambda _: "{url}?status__exact=draft".format(
                        url=reverse_lazy("admin:db_competencymatrixitemmodel_changelist"),
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
                "title": "Навигация",
                "items": [
                    {
                        "title": "Панель",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": "Матрица компетенций",
                        "icon": "school",
                        "link": reverse_lazy(
                            "admin:db_competencymatrixitemmodel_changelist",
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
