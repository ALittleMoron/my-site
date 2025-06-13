from dataclasses import dataclass
from unittest.mock import Mock

from dishka import AsyncContainer

from core.competency_matrix.use_cases import (
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
)
from db.storages.auth import AuthStorage
from entrypoints.auth.handlers import AuthHandler
from entrypoints.auth.utils import Hasher


@dataclass(kw_only=True)
class IocContainerHelper:
    container: AsyncContainer

    async def get_hasher(self) -> Hasher:
        return await self.container.get(Hasher)

    async def get_auth_handler(self) -> AuthHandler:
        return await self.container.get(AuthHandler)

    async def get_mock_get_item_use_case(self) -> Mock:
        return await self.container.get(AbstractGetItemUseCase)

    async def get_mock_list_items_use_case(self) -> Mock:
        return await self.container.get(AbstractListItemsUseCase)

    async def get_mock_list_sheets_use_case(self) -> Mock:
        return await self.container.get(AbstractListSheetsUseCase)

    async def get_auth_storage(self) -> Mock:
        return await self.container.get(AuthStorage)
