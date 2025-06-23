from dataclasses import dataclass
from typing import cast
from unittest.mock import Mock

from dishka import AsyncContainer

from core.competency_matrix.use_cases import (
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
)
from db.storages.auth import AuthStorage
from entrypoints.admin.auth.handlers import AuthHandler
from entrypoints.admin.auth.utils import Hasher


@dataclass(kw_only=True)
class IocContainerHelper:
    container: AsyncContainer

    async def get_hasher(self) -> Hasher:
        return await self.container.get(Hasher)

    async def get_auth_handler(self) -> AuthHandler:
        return await self.container.get(AuthHandler)

    async def get_mock_get_item_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractGetItemUseCase)
        return cast(Mock, use_case)

    async def get_mock_list_items_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractListItemsUseCase)
        return cast(Mock, use_case)

    async def get_mock_list_sheets_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractListSheetsUseCase)
        return cast(Mock, use_case)

    async def get_auth_storage(self) -> Mock:
        use_case = await self.container.get(AuthStorage)
        return cast(Mock, use_case)
