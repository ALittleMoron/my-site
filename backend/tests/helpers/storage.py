from core.competency_matrix.schemas import CompetencyMatrixItem
from db.models import CompetencyMatrixItemModel, ResourceModel


class StorageHelper:
    def create_competency_matrix_item(
        cls,
        item: CompetencyMatrixItem,
    ) -> CompetencyMatrixItemModel:
        model = CompetencyMatrixItemModel.from_domain_schema(item=item)
        model.save()
        model.resources.set(
            [ResourceModel.from_domain_schema(schema=resource) for resource in item.resources]
        )
        return model

    def create_competency_matrix_items(
        cls,
        items: list[CompetencyMatrixItem],
    ) -> list[CompetencyMatrixItemModel]:
        res = []
        for item in items:
            model = cls.create_competency_matrix_item(item=item)
            res.append(model)
        return res
