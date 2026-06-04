from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from core.competency_matrix.schemas import CompetencyMatrixItemFilters
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.schemas import NoteTreeItemData
from core.notes.storages import NotesStorage
from core.wiki_links.enums import WikiLinkTargetTypeEnum
from core.wiki_links.schemas import WikiLinkTargetGroup, WikiLinkTargets
from core.wiki_links.use_cases import WikiLinksUseCase
from tests.unit.fixtures import FactoryFixture


class TestWikiLinksUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.notes_storage = Mock(spec=NotesStorage)
        self.matrix_storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = WikiLinksUseCase(
            notes_storage=self.notes_storage,
            matrix_storage=self.matrix_storage,
        )

    async def test_lists_note_and_matrix_targets_for_authoring(self) -> None:
        now = datetime.now(tz=UTC)
        self.notes_storage.list_tree_items.return_value = [
            NoteTreeItemData(
                folder="Engineering",
                title="Typed notes",
                slug="typed-notes",
                publish_status=PublishStatusEnum.PUBLISHED,
                published_at=None,
                updated_at=now,
            ),
            NoteTreeItemData(
                folder="Engineering",
                title="Draft notes",
                slug="draft-notes",
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
                    type=WikiLinkTargetTypeEnum.NOTES,
                    slugs=["typed-notes", "draft-notes"],
                ),
                WikiLinkTargetGroup(
                    type=WikiLinkTargetTypeEnum.MATRIX,
                    slugs=["how-to-write-function", "draft-matrix-question"],
                ),
            ],
        )
        self.notes_storage.list_tree_items.assert_called_once_with(
            only_published=False,
            language=LanguageEnum.RU,
        )
        self.matrix_storage.list_competency_matrix_items.assert_called_once_with(
            filters=CompetencyMatrixItemFilters(only_published=False),
        )
