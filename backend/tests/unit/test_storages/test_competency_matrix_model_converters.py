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
            question="Question",
            resources=[
                self.factory.core.attached_external_resource(
                    resource_id=20,
                    name="Resource",
                    url="https://example.com",
                    context="Context",
                ),
            ],
        )

        model = CompetencyMatrixItemModel.from_domain_schema(
            item=item,
            include_relationships=False,
        )

        assert model.pk == item.id
        assert model.question == "Question"
        assert model.publish_status == PublishStatusEnum.PUBLISHED
        assert model.resource_links == []

    def test_resource_link_from_domain_schema_maps_attached_resource(self) -> None:
        resource = self.factory.core.attached_external_resource(
            resource_id=20,
            name="Resource",
            url="https://example.com",
            context="Context",
        )

        model = ResourceToItemSecondaryModel.from_domain_schema(schema=resource)

        assert model.resource_id == resource.id
        assert model.context == "Context"
        assert model.resource is not None
        assert model.resource.id == resource.id
        assert model.resource.name == "Resource"
        assert model.resource.url == "https://example.com"
