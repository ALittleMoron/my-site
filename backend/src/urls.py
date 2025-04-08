from django.conf import settings
from django.urls import include, path

from api.routers import api

urlpatterns = [
    path("api/", api.urls),
    path("", include("infra.urls")),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
