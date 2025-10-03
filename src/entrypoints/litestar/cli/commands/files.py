import io
import mimetypes

from config.constants import constants
from config.loggers import logger
from core.files.exceptions import FileStorageInternalError
from core.files.file_storages import FileStorage


async def collect_static(file_storage: FileStorage) -> None:
    await file_storage.ensure_namespace_exists(constants.minio_buckets.static)
    has_files = False

    for path in constants.path.static_dir.rglob("*"):
        if path.is_dir():
            continue
        if path.is_file():
            has_files = True
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            data = io.BytesIO(path.read_bytes())
            object_name = path.relative_to(constants.path.static_dir).as_posix()

            try:
                await file_storage.upload_file(
                    file_data=data,
                    object_name=object_name,
                    content_type=content_type,
                    namespace="static",
                )
                logger.info(f"Успешно добавлен файл по пути {object_name}")
            except FileStorageInternalError as e:
                logger.error(f"Ошибка загрузки файла: {e}")
        else:
            logger.warning(f"Непонятный тип: {path.name}")

    if not has_files:
        logger.warning("В папке нет файлов для загрузки!")
