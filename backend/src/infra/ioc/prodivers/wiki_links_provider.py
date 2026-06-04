from dishka import Provider, Scope, provide

from core.competency_matrix.storages import CompetencyMatrixStorage
from core.notes.storages import NotesStorage
from core.wiki_links.use_cases import AbstractWikiLinksUseCase, WikiLinksUseCase


class WikiLinksProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_wiki_links_use_case(
        self,
        notes_storage: NotesStorage,
        matrix_storage: CompetencyMatrixStorage,
    ) -> AbstractWikiLinksUseCase:
        return WikiLinksUseCase(
            notes_storage=notes_storage,
            matrix_storage=matrix_storage,
        )
