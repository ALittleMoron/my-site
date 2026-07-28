from urllib.parse import quote

from litestar.response import Stream

from core.knowledge.files.enums import KnowledgeFileKind
from core.knowledge.files.schemas import KnowledgeFileContent
from infra.config.constants import constants


def build_knowledge_file_content_response(*, result: KnowledgeFileContent) -> Stream:
    is_photo = result.file.kind == KnowledgeFileKind.PERSON_PHOTO
    safe_ascii_name = "".join(
        character if character.isascii() and (character.isalnum() or character in " ._-") else "_"
        for character in result.file.original_name
    ).strip()
    if not safe_ascii_name:
        safe_ascii_name = "download"
    content_disposition = (
        'inline; filename="photo.webp"'
        if is_photo
        else (
            f'attachment; filename="{safe_ascii_name}"; '
            f"filename*=UTF-8''{quote(result.file.original_name, safe='')}"
        )
    )
    return Stream(
        result.content,
        media_type="image/webp" if is_photo else "application/octet-stream",
        headers={
            constants.knowledge_files.content_disposition_header_name: content_disposition,
            constants.knowledge_files.content_type_options_header_name: (
                constants.knowledge_files.content_type_options_header_value
            ),
            constants.knowledge_files.cache_control_header_name: (
                constants.knowledge_files.no_store_header_value
            ),
        },
    )
