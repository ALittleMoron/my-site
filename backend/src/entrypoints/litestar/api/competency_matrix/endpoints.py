from dataclasses import dataclass
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.datastructures import State
from litestar.datastructures.upload_file import UploadFile
from litestar.di import Provide
from litestar.params import Body, FromPath, MultipartBody, QueryParameter

from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.competency_matrix.generators import ItemIdGenerator, ResourceIdGenerator
from core.competency_matrix.parsers import QuestionQueueImportParser
from core.competency_matrix.schemas import (
    CompetencyMatrixItemBySlugGetParams,
    CompetencyMatrixItemFilters,
    CompetencyMatrixItemGetParams,
    CompetencyMatrixItemPublishStatusSwitchParams,
    CompetencyMatrixResourceSearchParams,
    CompetencyMatrixWorkspaceFilters,
    QuestionQueueImportFile,
    QuestionSuggestionLimitParams,
)
from core.competency_matrix.use_cases import AbstractCompetencyMatrixUseCase
from core.i18n.enums import LanguageEnum
from core.types import IntId
from entrypoints.litestar.api.competency_matrix.dependencies import (
    provide_competency_matrix_item_draft_status_params,
    provide_competency_matrix_item_get_params,
    provide_competency_matrix_item_published_status_params,
    provide_competency_matrix_public_item_get_params,
    provide_competency_matrix_resource_search_params,
    provide_competency_matrix_workspace_filters,
    provide_question_suggestion_limit_params,
)
from entrypoints.litestar.api.competency_matrix.schemas import (
    CompetencyMatrixFilterOptionsResponseSchema,
    CompetencyMatrixItemDetailResponseSchema,
    CompetencyMatrixItemRequestSchema,
    CompetencyMatrixItemsListResponseSchema,
    CompetencyMatrixResourcesResponseSchema,
    CompetencyMatrixSheetsListResponseSchema,
    CompetencyMatrixWorkspaceResponseSchema,
    QuestionSuggestionRequestSchema,
    QueuedQuestionResponseSchema,
    QueuedQuestionsResponseSchema,
)
from entrypoints.litestar.guards import content_manager_guard
from entrypoints.litestar.response_cache import (
    ResponseCacheDomain,
    invalidate_and_enqueue_response_cache_warm_domain,
)
from infra.config.constants import constants
from infra.config.settings import settings


@dataclass(frozen=True, slots=True)
class QueuedQuestionsImportRequestSchema:
    file: UploadFile


class PublicCompetencyMatrixApiController(Controller):
    path = "/competency-matrix"
    tags = ["public competency matrix"]

    @get(
        "/sheets",
        description="Получение публичного списка листов матрицы компетенций.",
        name="public-competency-matrix-sheets-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.COMPETENCY_MATRIX.cache_key_builder,
    )
    async def list_competency_matrix_sheet(
        self,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixSheetsListResponseSchema:
        sheets = await use_case.list_sheets()
        return CompetencyMatrixSheetsListResponseSchema.from_domain_schema(
            schema=sheets,
            language=language,
        )

    @get(
        "/items",
        description="Получение публичного списка вопросов по матрице компетенций.",
        name="public-competency-matrix-items-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.COMPETENCY_MATRIX.cache_key_builder,
    )
    async def list_competency_matrix_items(
        self,
        sheet_key: Annotated[str, QueryParameter(name="sheetKey")],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemsListResponseSchema:
        filters = CompetencyMatrixItemFilters(sheet_key=sheet_key, only_published=True)
        items = await use_case.list_items(filters=filters)
        return CompetencyMatrixItemsListResponseSchema.from_domain_schema(
            sheet_key=sheet_key,
            schema=items,
            language=language,
        )

    @get(
        "/items/detail/{pk:int}",
        description="Получение публичной подробной информации о вопросе матрицы по id.",
        name="public-competency-matrix-item-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.COMPETENCY_MATRIX.cache_key_builder,
    )
    async def get_competency_matrix_item(
        self,
        pk: FromPath[int],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.get_item(
            params=CompetencyMatrixItemGetParams(
                item_id=IntId(pk),
                only_published=True,
            ),
        )
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
            schema=item,
            language=language,
        )

    @get(
        "/items/public/{slug:str}",
        description="Получение публичной подробной информации о вопросе матрицы по slug.",
        name="public-competency-matrix-public-item-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=settings.app.get_cache_duration(constants.response_cache.default_ttl_seconds),
        cache_key_builder=ResponseCacheDomain.COMPETENCY_MATRIX.cache_key_builder,
        dependencies={
            "params": Provide(
                provide_competency_matrix_public_item_get_params,
                sync_to_thread=False,
            ),
        },
    )
    async def get_public_competency_matrix_item(
        self,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        params: CompetencyMatrixItemBySlugGetParams,
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.get_item_by_slug(params=params)
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
            schema=item,
            language=language,
        )

    @post(
        "/question-suggestions",
        description="Анонимное предложение вопроса для матрицы компетенций.",
        name="public-competency-matrix-question-suggestion-create-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
        dependencies={
            "limit": Provide(
                provide_question_suggestion_limit_params,
                sync_to_thread=False,
            ),
        },
    )
    async def suggest_competency_matrix_question(
        self,
        data: Annotated[QuestionSuggestionRequestSchema, Body()],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        limit: QuestionSuggestionLimitParams,
    ) -> None:
        await use_case.suggest_question(params=data.to_schema(limit=limit))


class AdminCompetencyMatrixApiController(Controller):
    path = "/competency-matrix"
    tags = ["admin competency matrix"]
    guards = [content_manager_guard]

    @get(
        "/sheets",
        description="Получение админского списка листов матрицы компетенций.",
        name="admin-competency-matrix-sheets-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_competency_matrix_sheet(
        self,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixSheetsListResponseSchema:
        sheets = await use_case.list_sheets()
        return CompetencyMatrixSheetsListResponseSchema.from_domain_schema(
            schema=sheets,
            language=language,
        )

    @get(
        "/resources/search",
        description="Админский поиск вопросов по матрице компетенций по названию и url.",
        name="admin-competency-matrix-resources-search-api-handler",
        status_code=status_codes.HTTP_200_OK,
        dependencies={
            "params": Provide(
                provide_competency_matrix_resource_search_params,
                sync_to_thread=False,
            ),
        },
    )
    async def search_competency_matrix_resources(
        self,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        params: CompetencyMatrixResourceSearchParams,
    ) -> CompetencyMatrixResourcesResponseSchema:
        items = await use_case.find_resources(params=params)
        return CompetencyMatrixResourcesResponseSchema.from_domain_schema(
            schema=items,
            language=params.language,
        )

    @get(
        "/queued-questions",
        description="Получение очереди предложенных вопросов матрицы компетенций.",
        name="admin-competency-matrix-queued-questions-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_queued_competency_matrix_questions(
        self,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> QueuedQuestionsResponseSchema:
        questions = await use_case.list_queued_questions()
        return QueuedQuestionsResponseSchema.from_domain_schema(schema=questions)

    @post(
        "/queued-questions",
        description="Ручное добавление вопроса в очередь матрицы компетенций.",
        name="admin-competency-matrix-queued-question-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_queued_competency_matrix_question(
        self,
        data: Annotated[QuestionSuggestionRequestSchema, Body()],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> QueuedQuestionResponseSchema:
        question = await use_case.suggest_question(params=data.to_schema(limit=None))
        return QueuedQuestionResponseSchema.from_domain_schema(schema=question)

    @post(
        "/queued-questions/import",
        description="Импорт вопросов в очередь матрицы компетенций из файла.",
        name="admin-competency-matrix-queued-questions-import-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def import_queued_competency_matrix_questions(
        self,
        data: MultipartBody[QueuedQuestionsImportRequestSchema],
        parser: FromDishka[QuestionQueueImportParser],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> QueuedQuestionsResponseSchema:
        params = parser.parse(
            file=QuestionQueueImportFile(
                filename=data.file.filename,
                content=await data.file.read(),
            ),
        )
        questions = await use_case.import_queued_questions(params=params)
        return QueuedQuestionsResponseSchema.from_domain_schema(schema=questions)

    @delete(
        "/queued-questions/{pk:int}",
        description="Отклонение вопроса из очереди матрицы компетенций.",
        name="admin-competency-matrix-queued-question-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_queued_competency_matrix_question(
        self,
        pk: FromPath[int],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> None:
        await use_case.delete_queued_question(question_id=IntId(pk))

    @post(
        "/queued-questions/{pk:int}/create-item",
        description="Создание вопроса матрицы компетенций из очереди.",
        name="admin-competency-matrix-queued-question-create-item-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_competency_matrix_item_from_queue(  # noqa: PLR0913
        self,
        pk: FromPath[int],
        item_id_generator: FromDishka[ItemIdGenerator],
        resource_id_generator: FromDishka[ResourceIdGenerator],
        request: Request[JwtUser, Token | None, State],
        data: Annotated[CompetencyMatrixItemRequestSchema, Body()],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.create_item_from_queue(
            params=data.to_create_from_queue_schema(
                queued_question_id=IntId(pk),
                item_id_generator=item_id_generator,
                resource_id_generator=resource_id_generator,
            ),
        )
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
            schema=item,
            language=language,
        )

    @get(
        "/items/workspace",
        description="Получение админского рабочего списка вопросов матрицы компетенций.",
        name="admin-competency-matrix-items-workspace-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
        dependencies={
            "filters": Provide(
                provide_competency_matrix_workspace_filters,
                sync_to_thread=False,
            ),
        },
    )
    async def list_competency_matrix_workspace_items(
        self,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        filters: CompetencyMatrixWorkspaceFilters,
    ) -> CompetencyMatrixWorkspaceResponseSchema:
        workspace = await use_case.list_workspace_items(filters=filters)
        return CompetencyMatrixWorkspaceResponseSchema.from_domain_schema(schema=workspace)

    @get(
        "/items/filter-options",
        description="Получение значений фильтров рабочего списка вопросов матрицы.",
        name="admin-competency-matrix-items-filter-options-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_competency_matrix_workspace_filter_options(
        self,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixFilterOptionsResponseSchema:
        options = await use_case.list_workspace_filter_options(language=language)
        return CompetencyMatrixFilterOptionsResponseSchema.from_domain_schema(schema=options)

    @get(
        "/items",
        description="Получение админского списка вопросов по матрице компетенций.",
        name="admin-competency-matrix-items-list-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def list_competency_matrix_items(
        self,
        sheet_key: Annotated[str, QueryParameter(name="sheetKey")],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        only_published: Annotated[bool, QueryParameter(name="onlyPublished")],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemsListResponseSchema:
        filters = CompetencyMatrixItemFilters(
            sheet_key=sheet_key,
            only_published=only_published,
        )
        items = await use_case.list_items(filters=filters)
        return CompetencyMatrixItemsListResponseSchema.from_domain_schema(
            sheet_key=sheet_key,
            schema=items,
            language=language,
        )

    @post(
        "/items",
        description="Создание вопроса в матрице компетенций.",
        name="admin-competency-matrix-item-create-api-handler",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def create_competency_matrix_item(  # noqa: PLR0913
        self,
        item_id_generator: FromDishka[ItemIdGenerator],
        resource_id_generator: FromDishka[ResourceIdGenerator],
        request: Request[JwtUser, Token | None, State],
        data: Annotated[CompetencyMatrixItemRequestSchema, Body()],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.create_item(
            params=data.to_create_schema(
                item_id_generator=item_id_generator,
                resource_id_generator=resource_id_generator,
            ),
        )
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
            schema=item,
            language=language,
        )

    @get(
        "/items/detail/{pk:int}",
        description="Получение админской подробной информации о вопросе матрицы.",
        name="admin-competency-matrix-item-detail-api-handler",
        status_code=status_codes.HTTP_200_OK,
        dependencies={
            "params": Provide(
                provide_competency_matrix_item_get_params,
                sync_to_thread=False,
            ),
        },
    )
    async def get_competency_matrix_item(
        self,
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        params: CompetencyMatrixItemGetParams,
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.get_item(params=params)
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
            schema=item,
            language=language,
        )

    @put(
        "/items/detail/{pk:int}",
        description="Обновление вопроса в матрице компетенций.",
        name="admin-competency-matrix-item-update-api-handler",
        status_code=status_codes.HTTP_200_OK,
    )
    async def update_competency_matrix_item(  # noqa: PLR0913
        self,
        pk: FromPath[int],
        resource_id_generator: FromDishka[ResourceIdGenerator],
        request: Request[JwtUser, Token | None, State],
        data: Annotated[CompetencyMatrixItemRequestSchema, Body()],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        language: Annotated[LanguageEnum, QueryParameter(name="language")],
    ) -> CompetencyMatrixItemDetailResponseSchema:
        item = await use_case.update_item(
            params=data.to_update_schema(
                item_id=IntId(pk),
                resource_id_generator=resource_id_generator,
            ),
        )
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )
        return CompetencyMatrixItemDetailResponseSchema.from_domain_schema(
            schema=item,
            language=language,
        )

    @delete(
        "/items/detail/{pk:int}",
        description="Удаление вопроса в матрице компетенций.",
        name="admin-competency-matrix-item-delete-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_competency_matrix_item(
        self,
        pk: FromPath[int],
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
    ) -> None:
        await use_case.delete_item(item_id=IntId(pk))
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )

    @post(
        "/items/detail/{pk:int}/set-draft",
        description='Установка статуса "Черновик" на вопрос в матрице компетенций.',
        name="admin-competency-matrix-item-set-draft-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
        dependencies={
            "params": Provide(
                provide_competency_matrix_item_draft_status_params,
                sync_to_thread=False,
            ),
        },
    )
    async def set_draft_status_to_competency_matrix_item(
        self,
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        params: CompetencyMatrixItemPublishStatusSwitchParams,
    ) -> None:
        await use_case.switch_item_publish_status(params=params)
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )

    @post(
        "/items/detail/{pk:int}/set-published",
        description='Установка статуса "Опубликовано" на вопрос в матрице компетенций.',
        name="admin-competency-matrix-item-set-published-api-handler",
        status_code=status_codes.HTTP_204_NO_CONTENT,
        dependencies={
            "params": Provide(
                provide_competency_matrix_item_published_status_params,
                sync_to_thread=False,
            ),
        },
    )
    async def set_published_status_to_competency_matrix_item(
        self,
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[AbstractCompetencyMatrixUseCase],
        params: CompetencyMatrixItemPublishStatusSwitchParams,
    ) -> None:
        await use_case.switch_item_publish_status(params=params)
        await invalidate_and_enqueue_response_cache_warm_domain(
            request=request,
            domain=ResponseCacheDomain.COMPETENCY_MATRIX,
        )


api_router = DishkaRouter("", route_handlers=[PublicCompetencyMatrixApiController])
admin_router = DishkaRouter("", route_handlers=[AdminCompetencyMatrixApiController])
