from django.conf import settings
from django.urls import include, path

from api.app import ninja_app

urlpatterns = [
    path("api/", ninja_app.urls),
    path("", include("infra.urls")),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
