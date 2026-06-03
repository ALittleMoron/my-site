from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItemCreateParams,
    CompetencyMatrixItemFilters,
    CompetencyMatrixItems,
    CompetencyMatrixItemUpdateParams,
    CompetencyMatrixItemWriteParams,
    ExternalResources,
    PublishedCompetencyMatrixItemsForSeo,
    Sheets,
)
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.types import IntId, SearchName


class AbstractCompetencyMatrixUseCase(ABC):
    @abstractmethod
    async def list_sheets(self) -> Sheets:
        raise NotImplementedError

    @abstractmethod
    async def find_resources(
        self,
        *,
        search_name: SearchName,
        limit: int,
        language: LanguageEnum,
    ) -> ExternalResources:
        raise NotImplementedError

    @abstractmethod
    async def list_items(
        self,
        *,
        filters: CompetencyMatrixItemFilters,
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
    async def get_item_by_slug(
        self,
        *,
        slug: str,
        only_published: bool,
    ) -> CompetencyMatrixItem:
        raise NotImplementedError

    @abstractmethod
    async def list_published_items_for_seo(self) -> PublishedCompetencyMatrixItemsForSeo:
        raise NotImplementedError

    @abstractmethod
    async def create_item(
        self,
        *,
        params: CompetencyMatrixItemCreateParams,
    ) -> CompetencyMatrixItem:
        raise NotImplementedError

    @abstractmethod
    async def update_item(
        self,
        *,
        params: CompetencyMatrixItemUpdateParams,
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
        return await self.storage.list_sheets()

    async def find_resources(
        self,
        *,
        search_name: SearchName,
        limit: int,
        language: LanguageEnum,
    ) -> ExternalResources:
        return await self.storage.search_competency_matrix_resources(
            search_name=search_name.cleaned,
            limit=limit,
            language=language,
        )

    async def list_items(
        self,
        *,
        filters: CompetencyMatrixItemFilters,
    ) -> CompetencyMatrixItems:
        items = await self.storage.list_competency_matrix_items(filters=filters)
        matrix = CompetencyMatrixItems(values=items)
        return matrix.only_available() if filters.only_published is True else matrix

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

    async def get_item_by_slug(
        self,
        *,
        slug: str,
        only_published: bool,
    ) -> CompetencyMatrixItem:
        item = await self.storage.get_competency_matrix_item_by_slug(slug=slug)
        if only_published and not item.is_available():
            raise CompetencyMatrixItemNotFoundError
        return item

    async def list_published_items_for_seo(self) -> PublishedCompetencyMatrixItemsForSeo:
        items = await self.storage.list_competency_matrix_items(
            filters=CompetencyMatrixItemFilters(sheet_key=None, only_published=True),
        )
        return CompetencyMatrixItems(values=items).only_available().to_published_for_seo()

    async def create_item(
        self,
        *,
        params: CompetencyMatrixItemCreateParams,
    ) -> CompetencyMatrixItem:
        item = await self._build_item_from_params(params=params)
        return await self.storage.create_competency_matrix_item(item=item)

    async def update_item(
        self,
        *,
        params: CompetencyMatrixItemUpdateParams,
    ) -> CompetencyMatrixItem:
        item = await self._build_item_from_params(params=params)
        return await self.storage.update_competency_matrix_item(item=item)

    async def _build_item_from_params(
        self,
        *,
        params: CompetencyMatrixItemWriteParams,
    ) -> CompetencyMatrixItem:
        resource_ids_to_assign = params.get_resource_ids_to_assign()
        resources = (
            await self.storage.get_resources_by_ids(resource_ids=resource_ids_to_assign)
            if resource_ids_to_assign
            else ExternalResources(values=[])
        )
        if not resources.all_resources_exists_by_ids(ids=set(resource_ids_to_assign)):
            raise CompetencyMatrixItemNotFoundError
        return params.to_item(resources=resources)

    async def delete_item(self, *, item_id: IntId) -> None:
        await self.storage.delete_competency_matrix_item(item_id=item_id)

    async def switch_item_publish_status(
        self,
        *,
        item_id: IntId,
        publish_status: PublishStatusEnum,
    ) -> None:
        await self.storage.update_competency_matrix_item_publish_status(
            item_id=item_id,
            publish_status=publish_status,
        )
