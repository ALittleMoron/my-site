from django.urls import path

from .views import custom_markdown_upload_image

urlpatterns = [
    path(
        'markdown-upload-image/',
        custom_markdown_upload_image,
        name='custom_markdown_upload_image',
    ),
]
