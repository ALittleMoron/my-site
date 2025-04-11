from django.contrib import admin
from django.urls import path

from settings.config import config

from infra.views import custom_markdown_upload_image

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        config.martor.upload_url.lstrip("/"),
        custom_markdown_upload_image,
        name="custom_markdown_upload_image",
    ),
]
