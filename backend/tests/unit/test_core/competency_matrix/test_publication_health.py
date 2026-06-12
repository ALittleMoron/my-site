from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.schemas import CompetencyMatrixMissingFieldEnum
from core.enums import PublishStatusEnum
from tests.unit.fixtures import FactoryFixture


class TestCompetencyMatrixPublicationHealth(FactoryFixture):
    def test_published_item_with_missing_required_answer_is_not_public_ready(self) -> None:
        item = self.factory.core.competency_matrix_item(
            item_id=1,
            publish_status=PublishStatusEnum.PUBLISHED,
            grade=GradeEnum.JUNIOR,
            answer_en="",
        )

        assert item.is_available() is False
        assert CompetencyMatrixMissingFieldEnum.ANSWER_EN in item.missing_publication_fields()

    def test_resources_are_not_required_for_public_readiness(self) -> None:
        item = self.factory.core.competency_matrix_item(
            item_id=1,
            publish_status=PublishStatusEnum.PUBLISHED,
            grade=GradeEnum.JUNIOR,
            resources=[],
        )

        assert item.is_available() is True
        assert item.missing_publication_fields() == ()
