from datetime import date
from typing import Annotated

from litestar.params import QueryParameter

from core.i18n.enums import LanguageEnum
from core.notes.schemas import NoteFilters


def provide_note_filters(  # noqa: PLR0913
    page: Annotated[int, QueryParameter(name="page", ge=1)],
    page_size: Annotated[int, QueryParameter(name="pageSize", ge=1, le=100)],
    only_published: Annotated[bool, QueryParameter(name="onlyPublished")],
    language: Annotated[LanguageEnum, QueryParameter(name="language")],
    tag_slug: Annotated[str | None, QueryParameter(name="tagSlug")] = None,
    published_from: Annotated[date | None, QueryParameter(name="publishedFrom")] = None,
    published_to: Annotated[date | None, QueryParameter(name="publishedTo")] = None,
    search_query: Annotated[str | None, QueryParameter(name="searchQuery")] = None,
) -> NoteFilters:
    normalized_search_query = (
        search_query.strip() if search_query is not None and search_query.strip() else None
    )
    return NoteFilters(
        page=page,
        page_size=page_size,
        language=language,
        only_published=only_published,
        tag_slug=tag_slug,
        published_from=published_from,
        published_to=published_to,
        search_query=normalized_search_query,
        include_tags=True,
    )
