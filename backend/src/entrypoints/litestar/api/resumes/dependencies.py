from typing import Annotated

from litestar import Request
from litestar.datastructures import State
from litestar.params import QueryParameter

from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.resumes.schemas import ResumeFilters


def provide_resume_filters(
    request: Request[JwtUser, Token | None, State],
    page: Annotated[int, QueryParameter(name="page", ge=1)],
    page_size: Annotated[int, QueryParameter(name="pageSize", ge=1, le=100)],
) -> ResumeFilters:
    return ResumeFilters(
        page=page,
        page_size=page_size,
        search_query=None,
        author_username=request.user.username,
    )
