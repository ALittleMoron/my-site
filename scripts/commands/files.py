import io
import mimetypes
from pathlib import Path

from click import secho
from miniopy_async import Minio
from miniopy_async.error import MinioException

from config.settings import settings


async def collect_static(static_files_path: Path, client: Minio) -> None:
    if not await client.bucket_exists(settings.minio.bucket_names.static):
        await client.make_bucket(bucket_name=settings.minio.bucket_names.static)
    has_files = False
    for path in static_files_path.rglob("*"):
        if path.is_dir():
            continue
        elif path.is_file():
            has_files = True
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            data = io.BytesIO(path.read_bytes())
            object_name = path.relative_to(static_files_path).as_posix()
            try:
                await client.put_object(
                    bucket_name=settings.minio.bucket_names.static,
                    object_name=object_name,
                    data=data,
                    content_type=content_type,
                    length=path.stat().st_size,
                )
                secho(
                    f"Успешно добавлен файл по пути {object_name}",
                    fg="green",
                )
            except MinioException as e:
                secho(f"Ошибка запроса в Minio: {e}", fg="red")
        else:
            secho("Кто ты воин?")
    if not has_files:
        secho(f"В папке нет файлов для загрузки!", fg="yellow")
