from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.datastructures import State
from litestar.di import Provide
from litestar.params import Body, FromPath

from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.resumes.schemas import ResumeFilters
from core.resumes.use_cases import ResumesUseCase
from core.types import IntId
from entrypoints.litestar.api.resumes.dependencies import provide_resume_filters
from entrypoints.litestar.api.resumes.schemas import (
    ResumeRequestSchema,
    ResumeResponseSchema,
    ResumesResponseSchema,
)
from entrypoints.litestar.guards import admin_user_guard


class AdminResumesApiController(Controller):
    path = "/resumes"
    tags = ["admin resumes"]
    guards = [admin_user_guard]

    @get(
        "",
        description="Получение админского списка резюме.",
        name="admin-resumes-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        dependencies={"filters": Provide(provide_resume_filters, sync_to_thread=False)},
    )
    async def list_resumes(
        self,
        use_case: FromDishka[ResumesUseCase],
        filters: ResumeFilters,
    ) -> ResumesResponseSchema:
        resumes = await use_case.list_resumes(filters=filters)
        return ResumesResponseSchema.from_domain_schema(schema=resumes)

    @post(
        "",
        description="Создание резюме.",
        name="admin-resumes-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_resume(
        self,
        data: Annotated[ResumeRequestSchema, Body()],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[ResumesUseCase],
    ) -> ResumeResponseSchema:
        resume = await use_case.create_resume(
            params=data.to_create_schema(author_username=request.user.username),
        )
        return ResumeResponseSchema.from_domain_schema(schema=resume)

    @get(
        "/{resume_id:int}",
        description="Получение админской подробной информации о резюме.",
        name="admin-resumes-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_resume(
        self,
        resume_id: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[ResumesUseCase],
    ) -> ResumeResponseSchema:
        resume = await use_case.get_resume(
            resume_id=IntId(resume_id),
            author_username=request.user.username,
        )
        return ResumeResponseSchema.from_domain_schema(schema=resume)

    @put(
        "/{resume_id:int}",
        description="Обновление резюме.",
        name="admin-resumes-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_resume(
        self,
        resume_id: FromPath[int],
        data: Annotated[ResumeRequestSchema, Body()],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[ResumesUseCase],
    ) -> ResumeResponseSchema:
        resume = await use_case.update_resume(
            resume_id=IntId(resume_id),
            params=data.to_update_schema(),
            author_username=request.user.username,
        )
        return ResumeResponseSchema.from_domain_schema(schema=resume)

    @delete(
        "/{resume_id:int}",
        description="Удаление резюме.",
        name="admin-resumes-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_resume(
        self,
        resume_id: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[ResumesUseCase],
    ) -> None:
        await use_case.delete_resume(
            resume_id=IntId(resume_id),
            author_username=request.user.username,
        )


admin_router = DishkaRouter("", route_handlers=[AdminResumesApiController])
