import io
import json
import mimetypes
from pathlib import Path
from typing import Any

from click import secho
from miniopy_async.api import Minio
from miniopy_async.error import MinioException

from config.constants import constants


def create_bucket_policy(bucket_name: str) -> dict[str, Any]:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                "Resource": f"arn:aws:s3:::{bucket_name}",
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            },
        ],
    }



async def init_buckets(client: Minio) -> None:
    for bucket_name in [constants.minio_buckets.static, constants.minio_buckets.media]:
        if not await client.bucket_exists(bucket_name):
            await client.make_bucket(bucket_name=bucket_name)
        await client.set_bucket_policy(
            bucket_name=bucket_name,
            policy=json.dumps(create_bucket_policy(bucket_name=bucket_name)),
        )


async def collect_static(static_files_path: Path, client: Minio) -> None:
    if not await client.bucket_exists(constants.minio_buckets.static):
        await client.make_bucket(bucket_name=constants.minio_buckets.static)
    has_files = False
    for path in static_files_path.rglob("*"):
        if path.is_dir():
            continue
        if path.is_file():
            has_files = True
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            data = io.BytesIO(path.read_bytes())
            object_name = path.relative_to(static_files_path).as_posix()
            try:
                await client.put_object(
                    bucket_name=constants.minio_buckets.static,
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
        secho("В папке нет файлов для загрузки!", fg="yellow")
