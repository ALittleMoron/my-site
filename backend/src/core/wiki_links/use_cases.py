from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.competency_matrix.schemas import CompetencyMatrixItemFilters
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.i18n.enums import LanguageEnum
from core.notes.storages import NotesStorage
from core.wiki_links.enums import WikiLinkTargetTypeEnum
from core.wiki_links.schemas import WikiLinkTargetGroup, WikiLinkTargets


class AbstractWikiLinksUseCase(ABC):
    @abstractmethod
    async def list_targets(self, *, language: LanguageEnum) -> WikiLinkTargets:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class WikiLinksUseCase(AbstractWikiLinksUseCase):
    notes_storage: NotesStorage
    matrix_storage: CompetencyMatrixStorage

    async def list_targets(self, *, language: LanguageEnum) -> WikiLinkTargets:
        note_items = await self.notes_storage.list_tree_items(
            only_published=False,
            language=language,
        )
        matrix_items = await self.matrix_storage.list_competency_matrix_items(
            filters=CompetencyMatrixItemFilters(only_published=False),
        )
        return WikiLinkTargets(
            values=[
                WikiLinkTargetGroup(
                    type=WikiLinkTargetTypeEnum.NOTES,
                    slugs=[note.slug for note in note_items],
                ),
                WikiLinkTargetGroup(
                    type=WikiLinkTargetTypeEnum.MATRIX,
                    slugs=[item.slug for item in matrix_items],
                ),
            ],
        )
