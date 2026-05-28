from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItems,
    CompetencyMatrixItemUpsertParams,
    ExternalResources,
    Sheets,
)
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.enums import PublishStatusEnum
from core.types import IntId, SearchName


class AbstractCompetencyMatrixUseCase(ABC):
    @abstractmethod
    async def list_sheets(self) -> Sheets:
        raise NotImplementedError

    @abstractmethod
    async def find_resources(self, *, search_name: SearchName, limit: int) -> ExternalResources:
        raise NotImplementedError

    @abstractmethod
    async def list_items(
        self,
        *,
        sheet_name: str,
        only_published: bool,
    ) -> CompetencyMatrixItems:
        raise NotImplementedError

    @abstractmethod
    async def get_item(
        self,
        *,
        item_id: IntId,
        only_published: bool,
    ) -> CompetencyMatrixItem:
        raise NotImplementedError

    @abstractmethod
    async def upsert_item(
        self,
        *,
        params: CompetencyMatrixItemUpsertParams,
    ) -> CompetencyMatrixItem:
        raise NotImplementedError

    @abstractmethod
    async def delete_item(self, *, item_id: IntId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def switch_item_publish_status(
        self,
        *,
        item_id: IntId,
        publish_status: PublishStatusEnum,
    ) -> None:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class CompetencyMatrixUseCase(AbstractCompetencyMatrixUseCase):
    storage: CompetencyMatrixStorage

    async def list_sheets(self) -> Sheets:
        sheets = await self.storage.list_sheets()
        return Sheets(values=sheets)

    async def find_resources(
        self,
        *,
        search_name: SearchName,
        limit: int,
    ) -> ExternalResources:
        return await self.storage.search_competency_matrix_resources(
            search_name=search_name.cleaned,
            limit=limit,
        )

    async def list_items(
        self,
        *,
        sheet_name: str,
        only_published: bool,
    ) -> CompetencyMatrixItems:
        items = await self.storage.list_competency_matrix_items(sheet_name=sheet_name)
        matrix = CompetencyMatrixItems(values=items)
        return matrix.only_available() if only_published else matrix

    async def get_item(
        self,
        *,
        item_id: IntId,
        only_published: bool,
    ) -> CompetencyMatrixItem:
        item = await self.storage.get_competency_matrix_item(item_id=item_id)
        if only_published and not item.is_available():
            raise CompetencyMatrixItemNotFoundError
        return item

    async def upsert_item(
        self,
        *,
        params: CompetencyMatrixItemUpsertParams,
    ) -> CompetencyMatrixItem:
        resource_ids_to_assign = params.get_resource_ids_to_assign()
        resources = (
            await self.storage.get_resources_by_ids(resource_ids=resource_ids_to_assign)
            if resource_ids_to_assign
            else ExternalResources(values=[])
        )
        if not resources.all_resources_exists_by_ids(ids=set(resource_ids_to_assign)):
            raise CompetencyMatrixItemNotFoundError
        item = params.to_item(resources=resources)
        return await self.storage.upsert_competency_matrix_item(item=item)

    async def delete_item(self, *, item_id: IntId) -> None:
        await self.storage.delete_competency_matrix_item(item_id=item_id)

    async def switch_item_publish_status(
        self,
        *,
        item_id: IntId,
        publish_status: PublishStatusEnum,
    ) -> None:
        item = await self.storage.get_competency_matrix_item(item_id=item_id)
        item.set_publish_status(status=publish_status)
        await self.storage.upsert_competency_matrix_item(item=item)
