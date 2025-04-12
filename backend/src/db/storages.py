from abc import ABC, abstractmethod

from core.competency_matrix.exceptions import CompetencyMatrixItemNotFoundError
from core.competency_matrix.schemas import CompetencyMatrixItem
from db.models import CompetencyMatrixItemModel


class CompetencyMatrixStorage(ABC):
    @abstractmethod
    async def list_sheets(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def list_competency_matrix_items(self, sheet_name: str) -> list[CompetencyMatrixItem]:
        raise NotImplementedError

    @abstractmethod
    async def get_competency_matrix_item(self, item_id: int) -> CompetencyMatrixItem:
        raise NotImplementedError


class CompetencyMatrixDatabaseStorage(CompetencyMatrixStorage):
    async def list_sheets(self) -> list[str]:
        return [
            sheet_name
            async for sheet_name in (
                CompetencyMatrixItemModel.published.order_by("sheet")
                .distinct("sheet")
                .values_list(
                    "sheet",
                    flat=True,
                )
            )
        ]

    async def list_competency_matrix_items(self, sheet_name: str) -> list[CompetencyMatrixItem]:
        return [
            item.to_domain_schema()
            async for item in CompetencyMatrixItemModel.published.filter(
                sheet__iexact=sheet_name.lower(),
            )
        ]

    async def get_competency_matrix_item(self, item_id: int) -> CompetencyMatrixItem:
        try:
            item = await CompetencyMatrixItemModel.objects.aget(id=item_id)
            return item.to_domain_schema()
        except CompetencyMatrixItemModel.DoesNotExist as exc:
            raise CompetencyMatrixItemNotFoundError from exc
