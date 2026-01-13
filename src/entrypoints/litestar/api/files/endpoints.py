from typing import Annotated

from dishka.integrations.litestar import DishkaRouter, FromDishka
from litestar import get
from litestar.params import Parameter

from core.files.schemas import PresignPutObjectParams
from core.files.use_cases import AbstractPresignPutObjectUseCase
from entrypoints.litestar.api.files.schemas import FilePresignPutResponseSchema


@get(
    "/presign-put",
    description="Получение предподписанной ссылки для загрузки медиа-файла.",
)
async def presign_put_media_file(
    content_type: Annotated[str, Parameter(query="contentType")],
    use_case: FromDishka[AbstractPresignPutObjectUseCase],
) -> FilePresignPutResponseSchema:
    params = PresignPutObjectParams(
        content_type=content_type,
        folder="text-attachments",
        namespace="media",
    )
    urls = await use_case.execute(params=params)
    return FilePresignPutResponseSchema.from_schema(schema=urls)


api_router = DishkaRouter(
    "/files",
    route_handlers=[presign_put_media_file],
)
