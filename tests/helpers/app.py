import uuid
from dataclasses import dataclass
from typing import cast
from unittest.mock import Mock

from dishka import AsyncContainer

from core.auth.password_hashers import PasswordHasher
from core.auth.storages import AuthStorage
from core.auth.token_handlers import TokenHandler
from core.auth.use_cases import (
    AbstractLoginUseCase,
    AbstractAuthenticateUseCase,
    AbstractLogoutUseCase,
)
from core.competency_matrix.use_cases import (
    AbstractGetItemUseCase,
    AbstractListItemsUseCase,
    AbstractListSheetsUseCase,
)
from core.contacts.use_cases import AbstractCreateContactMeRequestUseCase
from core.files.file_name_generators import FileNameGenerator
from core.files.use_cases import AbstractPresignPutObjectUseCase


@dataclass(kw_only=True)
class IocContainerHelper:
    container: AsyncContainer

    # COMMON
    async def get_random_uuid(self) -> uuid.UUID:
        return await self.container.get(uuid.UUID)

    # CONTACTS
    async def get_create_contact_me_request_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractCreateContactMeRequestUseCase)
        return cast(Mock, use_case)

    # COMPETENCY MATRIX
    async def get_get_item_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractGetItemUseCase)
        return cast(Mock, use_case)

    async def get_list_items_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractListItemsUseCase)
        return cast(Mock, use_case)

    async def get_list_sheets_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractListSheetsUseCase)
        return cast(Mock, use_case)

    # AUTH
    async def get_hasher(self) -> Mock:
        hasher = await self.container.get(PasswordHasher)
        return cast(Mock, hasher)

    async def get_token_handler(self) -> Mock:
        handler = await self.container.get(TokenHandler)
        return cast(Mock, handler)

    async def get_auth_storage(self) -> Mock:
        storage = await self.container.get(AuthStorage)
        return cast(Mock, storage)

    async def get_login_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractLoginUseCase)
        return cast(Mock, use_case)

    async def get_logout_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractLogoutUseCase)
        return cast(Mock, use_case)

    async def get_authenticate_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractAuthenticateUseCase)
        return cast(Mock, use_case)

    # FILES
    async def get_file_name_generator(self) -> Mock:
        generator = await self.container.get(FileNameGenerator)
        return cast(Mock, generator)

    async def get_presign_put_url_use_case(self) -> Mock:
        use_case = await self.container.get(AbstractPresignPutObjectUseCase)
        return cast(Mock, use_case)
