import os
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from mdeditor.configs import MDConfig

MDEDITOR_CONFIGS = MDConfig('default')


@require_POST
@staff_member_required
@csrf_exempt
def custom_markdown_upload_image(request) -> HttpResponse:
    if 'editormd-image-file' not in request.FILES:
        return JsonResponse({'success': 0, 'message': "No file in request", 'url': ""})
    image = request.FILES['editormd-image-file']
    if isinstance(image, list):
        return JsonResponse({'success': 0, 'message': "List of files not permitted", 'url': ""})
    image_types = MDEDITOR_CONFIGS.get("upload_image_formats")
    if image_types is not None and image.content_type not in image_types:
        return JsonResponse({'success': 0, 'message': "Bad image format", 'url': ""})
    size = getattr(settings, "MAX_IMAGE_UPLOAD_SIZE", None)
    if size and image.size > size:
        msg = f'Maximum image file is {size / (1024 * 1024)} MB.'
        return JsonResponse({'success': 0, 'message': msg, 'url': ""})
    random_name = uuid.uuid4().hex + '-' + image.name.replace(' ', '_')
    current_date = datetime.now().strftime('%Y-%m-%d')
    upload_path = os.path.join(settings.MARTOR_UPLOAD_PATH, current_date, random_name)
    def_path = default_storage.save(name=upload_path, content=ContentFile(image.read()))
    image_url = ''.join([settings.MEDIA_URL, def_path])
    return JsonResponse(
        {
            'success': 1,
            'message': "Image was successfully uploaded.",
            'url': image_url,
        },
    )
