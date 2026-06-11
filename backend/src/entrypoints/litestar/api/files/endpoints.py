from typing import Annotated

from dishka.integrations.litestar import DishkaRouter, FromDishka
from litestar import Controller, get
from litestar.params import QueryParameter

from core.files.schemas import PresignPutObjectParams
from core.files.use_cases import AbstractFilesUseCase
from entrypoints.litestar.api.files.schemas import FilePresignPutResponseSchema
from entrypoints.litestar.guards import content_manager_guard


class FilesApiController(Controller):
    path = "/files"
    tags = ["admin files"]
    guards = [content_manager_guard]

    @get(
        "/presign-put",
        description="Получение предподписанной ссылки для загрузки медиа-файла.",
        name="admin-files-presign-put-api-handler",
    )
    async def presign_put_media_file(
        self,
        content_type: Annotated[str, QueryParameter(name="contentType")],
        use_case: FromDishka[AbstractFilesUseCase],
    ) -> FilePresignPutResponseSchema:
        params = PresignPutObjectParams(
            content_type=content_type,
            folder="text-attachments",
            namespace="media",
        )
        urls = await use_case.presign_put_object(params=params)
        return FilePresignPutResponseSchema.from_domain_schema(schema=urls)


admin_router = DishkaRouter("", route_handlers=[FilesApiController])
