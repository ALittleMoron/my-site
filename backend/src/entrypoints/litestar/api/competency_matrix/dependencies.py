from typing import Annotated

from litestar.params import FromPath, QueryParameter

from core.competency_matrix.schemas import (
    CompetencyMatrixItemBySlugGetParams,
    CompetencyMatrixItemGetParams,
    CompetencyMatrixItemPublishStatusSwitchParams,
    CompetencyMatrixResourceSearchParams,
)
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId, SearchName


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
    pk: FromPath[int],
    only_published: Annotated[bool, QueryParameter(name="onlyPublished")],
) -> CompetencyMatrixItemGetParams:
    return CompetencyMatrixItemGetParams(
        item_id=IntId(pk),
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
    pk: FromPath[int],
) -> CompetencyMatrixItemPublishStatusSwitchParams:
    return CompetencyMatrixItemPublishStatusSwitchParams(
        item_id=IntId(pk),
        publish_status=PublishStatusEnum.DRAFT,
    )


def provide_competency_matrix_item_published_status_params(
    pk: FromPath[int],
) -> CompetencyMatrixItemPublishStatusSwitchParams:
    return CompetencyMatrixItemPublishStatusSwitchParams(
        item_id=IntId(pk),
        publish_status=PublishStatusEnum.PUBLISHED,
    )
