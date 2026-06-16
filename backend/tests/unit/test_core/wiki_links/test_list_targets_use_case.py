from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from core.articles.schemas import ArticleTreeItemData
from core.articles.storages import ArticlesStorage
from core.competency_matrix.schemas import CompetencyMatrixItemFilters
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.wiki_links.enums import WikiLinkTargetTypeEnum
from core.wiki_links.schemas import WikiLinkTargetGroup, WikiLinkTargets
from core.wiki_links.use_cases import WikiLinksUseCase
from tests.unit.fixtures import FactoryFixture


class TestWikiLinksUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.articles_storage = Mock(spec=ArticlesStorage)
        self.matrix_storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = WikiLinksUseCase(
            articles_storage=self.articles_storage,
            matrix_storage=self.matrix_storage,
        )

    async def test_lists_article_and_matrix_targets_for_authoring(self) -> None:
        now = datetime.now(tz=UTC)
        self.articles_storage.list_tree_items.return_value = [
            ArticleTreeItemData(
                folder="Engineering",
                title="Typed articles",
                slug="typed-articles",
                publish_status=PublishStatusEnum.PUBLISHED,
                published_at=None,
                updated_at=now,
            ),
            ArticleTreeItemData(
                folder="Engineering",
                title="Draft articles",
                slug="draft-articles",
                publish_status=PublishStatusEnum.DRAFT,
                published_at=None,
                updated_at=now,
            ),
        ]
        self.matrix_storage.list_competency_matrix_items.return_value = [
            self.factory.core.competency_matrix_item(
                item_id=1,
                slug="how-to-write-function",
            ),
            self.factory.core.competency_matrix_item(
                item_id=2,
                slug="draft-matrix-question",
            ),
        ]

        result = await self.use_case.list_targets(language=LanguageEnum.RU)

        assert result == WikiLinkTargets(
            values=[
                WikiLinkTargetGroup(
                    type=WikiLinkTargetTypeEnum.ARTICLES,
                    slugs=["typed-articles", "draft-articles"],
                ),
                WikiLinkTargetGroup(
                    type=WikiLinkTargetTypeEnum.MATRIX,
                    slugs=["how-to-write-function", "draft-matrix-question"],
                ),
            ],
        )
        self.articles_storage.list_tree_items.assert_called_once_with(
            only_published=False,
            language=LanguageEnum.RU,
        )
        self.matrix_storage.list_competency_matrix_items.assert_called_once_with(
            filters=CompetencyMatrixItemFilters(only_published=False),
        )
