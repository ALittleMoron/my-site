import uuid
from dataclasses import dataclass
from typing import cast
from unittest.mock import Mock

from dishka import AsyncContainer

from core.auth.password_hashers import PasswordHasher
from core.auth.token_handlers import TokenHandler
from core.competency_matrix.use_cases import (
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
)
from core.contacts.use_cases import AbstractCreateContactMeRequestUseCase
from db.storages.auth import AuthStorage


@dataclass(kw_only=True)
class IocContainerHelper:
    container: AsyncContainer

    async def get_hasher(self) -> PasswordHasher:
        return await self.container.get(PasswordHasher)

    async def get_random_uuid(self) -> uuid.UUID:
        return await self.container.get(uuid.UUID)

    async def get_mock_create_contact_me_request_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractCreateContactMeRequestUseCase)
        return cast(Mock, use_case)

    async def get_auth_handler(self) -> TokenHandler:
        return await self.container.get(TokenHandler)

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
