# ruff: noqa: UP040
# Litestar 2.23 does not unwrap PEP 695 aliases in handler signatures.
from datetime import date, datetime
from typing import Annotated, TypeAlias

from litestar.enums import RequestEncodingType
from litestar.openapi.spec import Example
from litestar.params import BodyKwarg, PathParameter, QueryParameter

from core.calendar.enums import CalendarWindow
from core.competency_matrix.enums import (
    CompetencyMatrixWorkspaceSortEnum,
    GradeEnum,
    InterviewFrequencyEnum,
)
from core.enums import PublishStatusEnum
from core.files.enums import FilePurpose
from core.i18n.enums import LanguageEnum
from core.knowledge.dates.enums import KnowledgeDateListSort
from core.knowledge.people.enums import PersonListSort


def build_examples(*values: object) -> list[Example]:
    return [Example(value=value) for value in values]


def api_query_parameter(  # noqa: PLR0913
    *,
    name: str,
    title: str,
    description: str,
    examples: tuple[object, ...],
    ge: float | None,
    le: float | None,
    min_items: int | None,
    max_items: int | None,
) -> QueryParameter:
    return QueryParameter(
        name=name,
        title=title,
        description=description,
        examples=build_examples(*examples),
        ge=ge,
        le=le,
        min_items=min_items,
        max_items=max_items,
        schema_extra={"examples": list(examples)},
    )


def api_path_parameter(
    *,
    name: str,
    title: str,
    description: str,
    examples: tuple[object, ...],
) -> PathParameter:
    return PathParameter(
        name=name,
        title=title,
        description=description,
        examples=build_examples(*examples),
        schema_extra={"examples": list(examples)},
    )


def api_json_body(
    *,
    title: str,
    description: str,
    examples: tuple[object, ...],
) -> BodyKwarg:
    return BodyKwarg(
        title=title,
        description=description,
        examples=build_examples(*examples),
        media_type=RequestEncodingType.JSON,
        schema_extra={"examples": list(examples)},
    )


def api_multipart_body(
    *,
    title: str,
    description: str,
    examples: tuple[object, ...],
) -> BodyKwarg:
    return BodyKwarg(
        title=title,
        description=description,
        examples=build_examples(*examples),
        media_type=RequestEncodingType.MULTI_PART,
        schema_extra={"examples": list(examples)},
    )


PageQuery: TypeAlias = Annotated[
    int,
    api_query_parameter(
        name="page",
        title="Page",
        description="One-based page number.",
        examples=(1,),
        ge=1,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
PageSizeQuery: TypeAlias = Annotated[
    int,
    api_query_parameter(
        name="pageSize",
        title="Page size",
        description="Number of items to return per page.",
        examples=(20,),
        ge=1,
        le=100,
        min_items=None,
        max_items=None,
    ),
]
CalendarReferenceDateQuery: TypeAlias = Annotated[
    date,
    api_query_parameter(
        name="referenceDate",
        title="Calendar reference date",
        description="Browser-local date used to select the calendar window.",
        examples=("2026-07-31",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
CalendarWindowQuery: TypeAlias = Annotated[
    CalendarWindow,
    api_query_parameter(
        name="window",
        title="Calendar window",
        description="Single reference month or the reference and following months.",
        examples=(CalendarWindow.CURRENT_AND_NEXT_MONTHS.value,),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
PersonListSortQuery: TypeAlias = Annotated[
    PersonListSort,
    api_query_parameter(
        name="sort",
        title="People sort",
        description="Stable ordering for the private people workspace.",
        examples=(PersonListSort.UPDATED_NEWEST.value,),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
KnowledgeDateListSortQuery: TypeAlias = Annotated[
    KnowledgeDateListSort,
    api_query_parameter(
        name="sort",
        title="Dates sort",
        description="Stable ordering for the private memorable dates workspace.",
        examples=(KnowledgeDateListSort.DATE_ASC.value,),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
RelatedPersonIdQuery: TypeAlias = Annotated[
    str | None,
    api_query_parameter(
        name="relatedPersonId",
        title="Related person identifier",
        description="Optional author-scoped person backlink filter.",
        examples=("00000000000000000000000000000001",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
KnowledgeTagIdsQuery: TypeAlias = Annotated[
    list[str] | None,
    api_query_parameter(
        name="tagIds",
        title="Knowledge tag identifiers",
        description="Optional tag identifiers combined with AND semantics.",
        examples=(["00000000000000000000000000000001"],),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
LanguageQuery: TypeAlias = Annotated[
    LanguageEnum,
    api_query_parameter(
        name="language",
        title="Language",
        description="Language used for localized response fields.",
        examples=(LanguageEnum.RU.value, LanguageEnum.EN.value),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
OnlyPublishedQuery: TypeAlias = Annotated[
    bool,
    api_query_parameter(
        name="onlyPublished",
        title="Published only",
        description="Whether to include only published content.",
        examples=(True,),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
SearchNameQuery: TypeAlias = Annotated[
    str,
    api_query_parameter(
        name="searchName",
        title="Search name",
        description="Case-insensitive text used to search by display name.",
        examples=("python",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
SearchLimitQuery: TypeAlias = Annotated[
    int,
    api_query_parameter(
        name="limit",
        title="Search result limit",
        description="Maximum number of search matches to return.",
        examples=(10,),
        ge=1,
        le=50,
        min_items=None,
        max_items=None,
    ),
]
SearchQueryFilter: TypeAlias = Annotated[
    str | None,
    api_query_parameter(
        name="searchQuery",
        title="Search query",
        description="Optional free-text filter. Blank values are ignored.",
        examples=("async python",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
TagSlugQuery: TypeAlias = Annotated[
    str | None,
    api_query_parameter(
        name="tagSlug",
        title="Tag slug",
        description="Optional article tag slug filter.",
        examples=("python",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
PublishedFromQuery: TypeAlias = Annotated[
    date | None,
    api_query_parameter(
        name="publishedFrom",
        title="Published from",
        description="Optional inclusive publication date lower bound.",
        examples=("2026-01-01",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
PublishedToQuery: TypeAlias = Annotated[
    date | None,
    api_query_parameter(
        name="publishedTo",
        title="Published to",
        description="Optional inclusive publication date upper bound.",
        examples=("2026-01-31",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
DateFromQuery: TypeAlias = Annotated[
    date,
    api_query_parameter(
        name="dateFrom",
        title="Date from",
        description="Inclusive start date for the requested reporting period.",
        examples=("2026-01-01",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
DateToQuery: TypeAlias = Annotated[
    date,
    api_query_parameter(
        name="dateTo",
        title="Date to",
        description="Inclusive end date for the requested reporting period.",
        examples=("2026-01-31",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]

AgentClientIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="client_id",
        title="Agent client ID",
        description="Agent client identifier.",
        examples=("00000000000000000000000000000001",),
    ),
]
PersonIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="person_id",
        title="Person ID",
        description="Private person identifier.",
        examples=("00000000000000000000000000000001",),
    ),
]
KnowledgeDateIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="date_id",
        title="Knowledge date ID",
        description="Private memorable date identifier.",
        examples=("00000000000000000000000000000001",),
    ),
]
KnowledgeItemIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="item_id",
        title="Knowledge item ID",
        description="Private knowledge item identifier.",
        examples=("00000000000000000000000000000001",),
    ),
]
KnowledgeFileIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="file_id",
        title="Knowledge file ID",
        description="Private author-scoped knowledge file identifier.",
        examples=("00000000000000000000000000000001",),
    ),
]
KnowledgeTagIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="tag_id",
        title="Knowledge tag ID",
        description="Author-scoped knowledge tag identifier.",
        examples=("00000000000000000000000000000001",),
    ),
]
PersonRelationshipTypeIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="relationship_type_id",
        title="Person relationship type ID",
        description="Author-scoped relationship type identifier.",
        examples=("00000000000000000000000000000001",),
    ),
]
AgentAuditPageSizeQuery: TypeAlias = Annotated[
    int,
    api_query_parameter(
        name="pageSize",
        title="Audit page size",
        description="Number of newest audit events to return.",
        examples=(50,),
        ge=1,
        le=100,
        min_items=None,
        max_items=None,
    ),
]
AgentAuditCursorCreatedAtQuery: TypeAlias = Annotated[
    datetime | None,
    api_query_parameter(
        name="cursorCreatedAt",
        title="Audit cursor timestamp",
        description="Timestamp of the last event returned by the previous page.",
        examples=("2026-07-14T12:00:00+00:00",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
AgentAuditCursorEventIdQuery: TypeAlias = Annotated[
    str | None,
    api_query_parameter(
        name="cursorEventId",
        title="Audit cursor event ID",
        description="Identifier of the last event returned by the previous page.",
        examples=("00000000000000000000000000000001",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
ArticleIdsQuery: TypeAlias = Annotated[
    list[str],
    api_query_parameter(
        name="articleIds",
        title="Article identifiers",
        description="Article identifiers to include in the public statistics response.",
        examples=(["00000000000000000000000000000001"],),
        ge=None,
        le=None,
        min_items=1,
        max_items=None,
    ),
]
SheetKeyQuery: TypeAlias = Annotated[
    str,
    api_query_parameter(
        name="sheetKey",
        title="Sheet key",
        description="Stable language-neutral competency matrix sheet key.",
        examples=("python",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
FilePurposeQuery: TypeAlias = Annotated[
    FilePurpose,
    api_query_parameter(
        name="purpose",
        title="File purpose",
        description="Managed-file purpose namespace.",
        examples=(FilePurpose.ARTICLE_COVER_IMAGE.value,),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
MatrixWorkspaceSortQuery: TypeAlias = Annotated[
    CompetencyMatrixWorkspaceSortEnum,
    api_query_parameter(
        name="sort",
        title="Sort order",
        description="Sort mode for the competency matrix workspace list.",
        examples=("newest",),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
MatrixSheetKeysQuery: TypeAlias = Annotated[
    list[str] | None,
    api_query_parameter(
        name="sheetKeys",
        title="Sheet keys",
        description="Optional competency matrix sheet key filters.",
        examples=(["python"],),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
MatrixGradesQuery: TypeAlias = Annotated[
    list[GradeEnum] | None,
    api_query_parameter(
        name="grades",
        title="Grades",
        description="Optional competency grade filters.",
        examples=([GradeEnum.MIDDLE.value],),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
MatrixInterviewFrequenciesQuery: TypeAlias = Annotated[
    list[InterviewFrequencyEnum] | None,
    api_query_parameter(
        name="interviewFrequencies",
        title="Interview frequencies",
        description="Optional interview-frequency filters.",
        examples=([InterviewFrequencyEnum.OFTEN.value],),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
MatrixSectionIdsQuery: TypeAlias = Annotated[
    list[str] | None,
    api_query_parameter(
        name="sectionIds",
        title="Section IDs",
        description="Optional stable competency matrix section ID filters.",
        examples=(["00000000000000000000000000000001"],),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
MatrixSubsectionIdsQuery: TypeAlias = Annotated[
    list[str] | None,
    api_query_parameter(
        name="subsectionIds",
        title="Subsection IDs",
        description="Optional stable competency matrix subsection ID filters.",
        examples=(["00000000000000000000000000000001"],),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
MatrixSectionsQuery: TypeAlias = Annotated[
    list[str] | None,
    api_query_parameter(
        name="sections",
        title="Sections",
        description="Optional localized section name filters.",
        examples=(["Backend"],),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
MatrixSubsectionsQuery: TypeAlias = Annotated[
    list[str] | None,
    api_query_parameter(
        name="subsections",
        title="Subsections",
        description="Optional localized subsection name filters.",
        examples=(["Async IO"],),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
PublishStatusesQuery: TypeAlias = Annotated[
    list[PublishStatusEnum] | None,
    api_query_parameter(
        name="publishStatuses",
        title="Publication statuses",
        description="Optional publication status filters.",
        examples=([PublishStatusEnum.PUBLISHED.value],),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
PublishStatusQuery: TypeAlias = Annotated[
    PublishStatusEnum | None,
    api_query_parameter(
        name="publishStatus",
        title="Publication status",
        description="Optional exact publication status filter.",
        examples=(PublishStatusEnum.DRAFT.value,),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]
HasMissingFieldsQuery: TypeAlias = Annotated[
    bool | None,
    api_query_parameter(
        name="hasMissingFields",
        title="Has missing fields",
        description="Optional filter for competency matrix items with missing publication fields.",
        examples=(False,),
        ge=None,
        le=None,
        min_items=None,
        max_items=None,
    ),
]

ArticleSlugPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="slug",
        title="Article slug",
        description="URL slug of the article.",
        examples=("how-this-site-is-built",),
    ),
]
MatrixItemSlugPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="slug",
        title="Competency matrix question slug",
        description="URL slug of the public competency matrix question.",
        examples=("python-asyncio-task-gather",),
    ),
]
UsernamePath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="username",
        title="Username",
        description="Managed account username.",
        examples=("moderator",),
    ),
]
SessionIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="session_id",
        title="Session identifier",
        description="Hex identifier of the managed account session.",
        examples=("00000000000000000000000000000001",),
    ),
]
EntityPkPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="pk",
        title="Entity identifier",
        description="Hex identifier of the target entity.",
        examples=("00000000000000000000000000000001",),
    ),
]
SheetIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="sheet_id",
        title="Sheet identifier",
        description="Hex identifier of the competency matrix sheet.",
        examples=("00000000000000000000000000000001",),
    ),
]
SectionIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="section_id",
        title="Section identifier",
        description="Hex identifier of the competency matrix section.",
        examples=("00000000000000000000000000000002",),
    ),
]
FileIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="file_id",
        title="File identifier",
        description="Managed file identifier.",
        examples=("00000000000000000000000000000003",),
    ),
]
ResumeIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="resume_id",
        title="Resume identifier",
        description="Resume workspace identifier.",
        examples=("00000000000000000000000000000004",),
    ),
]
TagIdPath: TypeAlias = Annotated[
    str,
    api_path_parameter(
        name="tag_id",
        title="Tag identifier",
        description="Article tag identifier.",
        examples=("00000000000000000000000000000005",),
    ),
]
I18nLanguagePath: TypeAlias = Annotated[
    LanguageEnum,
    api_path_parameter(
        name="language",
        title="Language",
        description="Interface language code for the requested i18n bundle.",
        examples=(LanguageEnum.RU.value, LanguageEnum.EN.value),
    ),
]
