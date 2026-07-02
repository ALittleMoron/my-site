from datetime import UTC, date, datetime
from typing import Annotated

from litestar import Request
from litestar.datastructures import State
from litestar.params import FromPath, QueryParameter

from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.competency_matrix.enums import (
    CompetencyMatrixWorkspaceSortEnum,
    GradeEnum,
    InterviewFrequencyEnum,
)
from core.competency_matrix.schemas import (
    CompetencyMatrixItemBySlugGetParams,
    CompetencyMatrixItemGetParams,
    CompetencyMatrixItemPublishStatusSwitchParams,
    CompetencyMatrixResourceSearchParams,
    CompetencyMatrixWorkspaceFilters,
    QuestionSuggestionLimitParams,
)
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import SearchName


def provide_competency_matrix_resource_search_params(
    search_name: Annotated[str, QueryParameter(name="searchName")],
    limit: Annotated[int, QueryParameter(name="limit", ge=1, le=50)],
    language: Annotated[LanguageEnum, QueryParameter(name="language")],
) -> CompetencyMatrixResourceSearchParams:
    return CompetencyMatrixResourceSearchParams(
        search_name=SearchName(search_name),
        limit=limit,
        language=language,
    )


def provide_competency_matrix_item_get_params(
    pk: FromPath[str],
    only_published: Annotated[bool, QueryParameter(name="onlyPublished")],
) -> CompetencyMatrixItemGetParams:
    return CompetencyMatrixItemGetParams(
        item_id=pk,
        only_published=only_published,
    )


def provide_competency_matrix_public_item_get_params(
    slug: FromPath[str],
) -> CompetencyMatrixItemBySlugGetParams:
    return CompetencyMatrixItemBySlugGetParams(
        slug=slug,
        only_published=True,
    )


def provide_competency_matrix_item_draft_status_params(
    pk: FromPath[str],
) -> CompetencyMatrixItemPublishStatusSwitchParams:
    return CompetencyMatrixItemPublishStatusSwitchParams(
        item_id=pk,
        publish_status=PublishStatusEnum.DRAFT,
    )


def provide_competency_matrix_item_published_status_params(
    pk: FromPath[str],
) -> CompetencyMatrixItemPublishStatusSwitchParams:
    return CompetencyMatrixItemPublishStatusSwitchParams(
        item_id=pk,
        publish_status=PublishStatusEnum.PUBLISHED,
    )


def provide_competency_matrix_workspace_filters(  # noqa: PLR0913
    page: Annotated[int, QueryParameter(name="page", ge=1)],
    page_size: Annotated[int, QueryParameter(name="pageSize", ge=1, le=100)],
    language: Annotated[LanguageEnum, QueryParameter(name="language")],
    sort: Annotated[CompetencyMatrixWorkspaceSortEnum, QueryParameter(name="sort")],
    search_query: Annotated[str | None, QueryParameter(name="searchQuery")] = None,
    sheet_keys: Annotated[list[str] | None, QueryParameter(name="sheetKeys")] = None,
    grades: Annotated[list[GradeEnum] | None, QueryParameter(name="grades")] = None,
    interview_frequencies: Annotated[
        list[InterviewFrequencyEnum] | None,
        QueryParameter(name="interviewFrequencies"),
    ] = None,
    sections: Annotated[list[str] | None, QueryParameter(name="sections")] = None,
    subsections: Annotated[list[str] | None, QueryParameter(name="subsections")] = None,
    publish_statuses: Annotated[
        list[PublishStatusEnum] | None,
        QueryParameter(name="publishStatuses"),
    ] = None,
    published_from: Annotated[date | None, QueryParameter(name="publishedFrom")] = None,
    published_to: Annotated[date | None, QueryParameter(name="publishedTo")] = None,
    has_missing_fields: Annotated[
        bool | None,
        QueryParameter(name="hasMissingFields"),
    ] = None,
) -> CompetencyMatrixWorkspaceFilters:
    normalized_search_query = (
        search_query.strip() if search_query is not None and search_query.strip() else None
    )
    return CompetencyMatrixWorkspaceFilters(
        page=page,
        page_size=page_size,
        language=language,
        sort=sort,
        search_query=normalized_search_query,
        sheet_keys=tuple(sheet_keys or ()),
        grades=tuple(grades or ()),
        interview_frequencies=tuple(interview_frequencies or ()),
        sections=tuple(sections or ()),
        subsections=tuple(subsections or ()),
        publish_statuses=tuple(publish_statuses or ()),
        published_from=published_from,
        published_to=published_to,
        has_missing_fields=has_missing_fields,
    )


def provide_question_suggestion_limit_params(
    request: Request[JwtUser, Token | None, State],
) -> QuestionSuggestionLimitParams:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for is not None:
        forwarded_client = forwarded_for.split(",", maxsplit=1)[0].strip()
        if forwarded_client:
            return QuestionSuggestionLimitParams(
                client_identifier=forwarded_client,
                now=datetime.now(tz=UTC),
            )
    real_ip = request.headers.get("x-real-ip")
    if real_ip is not None:
        real_client = real_ip.strip()
        if real_client:
            return QuestionSuggestionLimitParams(
                client_identifier=real_client,
                now=datetime.now(tz=UTC),
            )
    return QuestionSuggestionLimitParams(
        client_identifier=request.client.host if request.client is not None else "",
        now=datetime.now(tz=UTC),
    )
