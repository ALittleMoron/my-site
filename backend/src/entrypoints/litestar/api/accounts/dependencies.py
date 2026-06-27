from typing import Annotated

from litestar.params import QueryParameter

from core.account.schemas import ManagedAccountFilters


def provide_managed_account_filters(
    page: Annotated[int, QueryParameter(name="page", ge=1)],
    page_size: Annotated[int, QueryParameter(name="pageSize", ge=1, le=100)],
) -> ManagedAccountFilters:
    return ManagedAccountFilters(page=page, page_size=page_size)
