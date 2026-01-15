from typing import Annotated

from dishka.integrations.litestar import DishkaRouter, FromDishka
from litestar import Controller, get
from litestar.params import Parameter

from core.files.schemas import PresignPutObjectParams
from core.files.use_cases import AbstractPresignPutObjectUseCase
from entrypoints.litestar.api.files.schemas import FilePresignPutResponseSchema
from entrypoints.litestar.guards import admin_user_guard


class FilesController(Controller):
    path = "/files"
    tags = ["files"]
    guards = [admin_user_guard]

    @get(
        "/presign-put",
        description="Получение предподписанной ссылки для загрузки медиа-файла.",
    )
    async def presign_put_media_file(
        self,
        content_type: Annotated[str, Parameter(query="contentType")],
        use_case: FromDishka[AbstractPresignPutObjectUseCase],
    ) -> FilePresignPutResponseSchema:
        params = PresignPutObjectParams(
            content_type=content_type,
            folder="text-attachments",
            namespace="media",
        )
        urls = await use_case.execute(params=params)
        return FilePresignPutResponseSchema.from_domain_schema(schema=urls)


api_router = DishkaRouter("", route_handlers=[FilesController])
