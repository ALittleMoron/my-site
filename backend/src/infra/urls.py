from django.contrib import admin
from django.urls import path

from infra.views import custom_markdown_upload_image
from settings.config import config

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        config.martor.upload_url.lstrip("/"),
        custom_markdown_upload_image,
        name="custom_markdown_upload_image",
    ),
]
