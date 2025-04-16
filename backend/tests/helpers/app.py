from dataclasses import dataclass

from dishka import AsyncContainer

from tests.mocks.competency_matrix.use_cases import (
    MockGetItemUseCase,
    MockListItemsUseCase,
    MockListSheetsUseCase,
)


@dataclass(kw_only=True)
class AppHelper:
    container: AsyncContainer

    async def get_mock_get_item_use_case(self) -> MockGetItemUseCase:
        return await self.container.get(MockGetItemUseCase)

    async def get_mock_list_items_use_case(self) -> MockListItemsUseCase:
        return await self.container.get(MockListItemsUseCase)

    async def get_mock_list_sheets_use_case(self) -> MockListSheetsUseCase:
        return await self.container.get(MockListSheetsUseCase)
