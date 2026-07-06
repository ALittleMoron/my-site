from litestar import Request
from litestar.datastructures import State

from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.resumes.schemas import ResumeFilters
from entrypoints.litestar.api.parameters import PageQuery, PageSizeQuery


def provide_resume_filters(
    request: Request[JwtUser, Token | None, State],
    page: PageQuery,
    page_size: PageSizeQuery,
) -> ResumeFilters:
    return ResumeFilters(
        page=page,
        page_size=page_size,
        search_query=None,
        author_username=request.user.username,
    )
