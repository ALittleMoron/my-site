from collections.abc import Sequence

from entrypoints.litestar.api.competency_matrix.endpoints import CompetencyMatrixApiController
from entrypoints.litestar.api.files.endpoints import FilesApiController
from entrypoints.litestar.api.notes.endpoints import NotesApiController
from entrypoints.litestar.api.wiki_links.endpoints import WikiLinksApiController
from entrypoints.litestar.guards import content_manager_guard


def assert_has_content_manager_guard(guards: Sequence[object] | None) -> None:
    assert guards is not None
    assert content_manager_guard in guards


class TestContentAccessRoutes:
    def test_notes_mutation_and_stats_handlers_use_content_manager_guard(self) -> None:
        for handler_name in (
            "create_note",
            "get_stats",
            "update_note",
            "delete_note",
            "set_draft_status_to_note",
            "set_published_status_to_note",
            "create_tag",
            "update_tag",
            "delete_tag",
            "restore_tag",
        ):
            assert_has_content_manager_guard(getattr(NotesApiController, handler_name).guards)

    def test_matrix_mutation_handlers_use_content_manager_guard(self) -> None:
        for handler_name in (
            "create_competency_matrix_item",
            "update_competency_matrix_item",
            "delete_competency_matrix_item",
            "set_draft_status_to_competency_matrix_item",
            "set_published_status_to_competency_matrix_item",
        ):
            assert_has_content_manager_guard(
                getattr(CompetencyMatrixApiController, handler_name).guards,
            )

    def test_file_upload_controller_uses_content_manager_guard(self) -> None:
        assert FilesApiController.guards == [content_manager_guard]

    def test_wiki_link_targets_handler_uses_content_manager_guard(self) -> None:
        assert_has_content_manager_guard(WikiLinksApiController.list_wiki_link_targets.guards)
