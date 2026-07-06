from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.datastructures import State
from litestar.di import NamedDependency, Provide

from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.resumes.schemas import ResumeFilters
from core.resumes.use_cases import ResumesUseCase
from entrypoints.litestar.api.parameters import ResumeIdPath, api_json_body
from entrypoints.litestar.api.resumes.dependencies import provide_resume_filters
from entrypoints.litestar.api.resumes.responses import ResumeExportResponse
from entrypoints.litestar.api.resumes.schemas import (
    ResumeExportRequestSchema,
    ResumeRequestSchema,
    ResumeResponseSchema,
    ResumesResponseSchema,
)
from entrypoints.litestar.guards import team_manager_guard


class AdminResumesApiController(Controller):
    path = "/resumes"
    tags = ["admin resumes"]
    guards = [team_manager_guard]

    @get(
        "",
        description="Get the admin resume list.",
        name="admin-resumes-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        dependencies={"filters": Provide(provide_resume_filters, sync_to_thread=False)},
    )
    async def list_resumes(
        self,
        use_case: FromDishka[ResumesUseCase],
        filters: NamedDependency[ResumeFilters],
    ) -> ResumesResponseSchema:
        resumes = await use_case.list_resumes(filters=filters)
        return ResumesResponseSchema.from_domain_schema(schema=resumes)

    @post(
        "",
        description="Create a resume.",
        name="admin-resumes-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_resume(
        self,
        data: Annotated[
            ResumeRequestSchema,
            api_json_body(
                title="Resume request",
                description="Structured resume workspace payload.",
                examples=(
                    {
                        "title": "Backend Engineer",
                        "language": "en",
                        "content": {
                            "profile": {
                                "fullName": "Dmitriy Lunev",
                                "headline": "Backend Engineer",
                                "location": "Moscow",
                                "email": "example@mail.ru",
                                "phone": "",
                                "telegram": "@alm_dmitriy_dev",
                                "website": "https://example.com",
                            },
                            "summary": {"text": "Builds reliable backend systems."},
                            "skills": [],
                            "experience": [],
                            "education": [],
                            "languages": [],
                            "certifications": [],
                            "additionalSections": [],
                        },
                    },
                ),
            ),
        ],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[ResumesUseCase],
    ) -> ResumeResponseSchema:
        resume = await use_case.create_resume(
            params=data.to_create_schema(author_username=request.user.username),
        )
        return ResumeResponseSchema.from_domain_schema(schema=resume)

    @get(
        "/{resume_id:str}",
        description="Get admin resume details.",
        name="admin-resumes-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def get_resume(
        self,
        resume_id: ResumeIdPath,
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[ResumesUseCase],
    ) -> ResumeResponseSchema:
        resume = await use_case.get_resume(
            resume_id=resume_id,
            author_username=request.user.username,
        )
        return ResumeResponseSchema.from_domain_schema(schema=resume)

    @put(
        "/{resume_id:str}",
        description="Update a resume.",
        name="admin-resumes-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_resume(
        self,
        resume_id: ResumeIdPath,
        data: Annotated[
            ResumeRequestSchema,
            api_json_body(
                title="Resume request",
                description="Structured resume workspace payload.",
                examples=(
                    {
                        "title": "Backend Engineer",
                        "language": "en",
                        "content": {
                            "profile": {
                                "fullName": "Dmitriy Lunev",
                                "headline": "Backend Engineer",
                                "location": "Moscow",
                                "email": "example@mail.ru",
                                "phone": "",
                                "telegram": "@alm_dmitriy_dev",
                                "website": "https://example.com",
                            },
                            "summary": {"text": "Builds reliable backend systems."},
                            "skills": [],
                            "experience": [],
                            "education": [],
                            "languages": [],
                            "certifications": [],
                            "additionalSections": [],
                        },
                    },
                ),
            ),
        ],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[ResumesUseCase],
    ) -> ResumeResponseSchema:
        resume = await use_case.update_resume(
            resume_id=resume_id,
            params=data.to_update_schema(),
            author_username=request.user.username,
        )
        return ResumeResponseSchema.from_domain_schema(schema=resume)

    @post(
        "/{resume_id:str}/export",
        description="Export a resume.",
        name="admin-resumes-export-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def export_resume(
        self,
        resume_id: ResumeIdPath,
        data: Annotated[
            ResumeExportRequestSchema,
            api_json_body(
                title="Resume export request",
                description="Structured resume payload plus requested export format.",
                examples=(
                    {
                        "title": "Backend Engineer",
                        "language": "en",
                        "format": "docx",
                        "content": {
                            "profile": {
                                "fullName": "Dmitriy Lunev",
                                "headline": "Backend Engineer",
                                "location": "Moscow",
                                "email": "example@mail.ru",
                                "phone": "",
                                "telegram": "@alm_dmitriy_dev",
                                "website": "https://example.com",
                            },
                            "summary": {"text": "Builds reliable backend systems."},
                            "skills": [],
                            "experience": [],
                            "education": [],
                            "languages": [],
                            "certifications": [],
                            "additionalSections": [],
                        },
                    },
                ),
            ),
        ],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[ResumesUseCase],
    ) -> ResumeExportResponse:
        document = await use_case.export_resume(
            resume_id=resume_id,
            params=data.to_export_schema(),
            author_username=request.user.username,
        )
        return ResumeExportResponse.from_resume_export(
            resume_id=resume_id,
            document=document,
        )

    @delete(
        "/{resume_id:str}",
        description="Delete a resume.",
        name="admin-resumes-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_resume(
        self,
        resume_id: ResumeIdPath,
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[ResumesUseCase],
    ) -> None:
        await use_case.delete_resume(
            resume_id=resume_id,
            author_username=request.user.username,
        )


admin_router = DishkaRouter("", route_handlers=[AdminResumesApiController])
