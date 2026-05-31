from core.enums import PublishStatusEnum
from infra.postgresql.models.competency_matrix import (
    CompetencyMatrixItemModel,
    ResourceToItemSecondaryModel,
)
from tests.fixtures import FactoryFixture


class TestCompetencyMatrixModelConverters(FactoryFixture):
    def test_item_from_domain_schema_can_skip_relationships(self) -> None:
        item = self.factory.core.competency_matrix_item(
            item_id=10,
            question_ru="Вопрос",
            question_en="Question",
            resources=[
                self.factory.core.attached_external_resource(
                    resource_id=20,
                    name_ru="Ресурс",
                    name_en="Resource",
                    url="https://example.com",
                    context_ru="Контекст",
                    context_en="Context",
                ),
            ],
        )

        model = CompetencyMatrixItemModel.from_domain_schema(
            item=item,
            include_relationships=False,
        )

        assert model.pk == item.id
        assert model.question_ru == "Вопрос"
        assert model.question_en == "Question"
        assert model.publish_status == PublishStatusEnum.PUBLISHED
        assert model.resource_links == []

    def test_resource_link_from_domain_schema_maps_attached_resource(self) -> None:
        resource = self.factory.core.attached_external_resource(
            resource_id=20,
            name_ru="Ресурс",
            name_en="Resource",
            url="https://example.com",
            context_ru="Контекст",
            context_en="Context",
        )

        model = ResourceToItemSecondaryModel.from_domain_schema(schema=resource)

        assert model.resource_id == resource.id
        assert model.context_ru == "Контекст"
        assert model.context_en == "Context"
        assert model.resource is not None
        assert model.resource.id == resource.id
        assert model.resource.name_ru == "Ресурс"
        assert model.resource.name_en == "Resource"
        assert model.resource.url == "https://example.com"
