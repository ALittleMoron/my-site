from core.auth.enums import RoleEnum
from core.competency_matrix.enums import GradeEnum
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from entrypoints.litestar.api.i18n.catalog import get_i18n_messages


class TestI18nCatalog:
    def test_all_supported_languages_have_same_keys(self) -> None:
        russian_keys = set(get_i18n_messages(language=LanguageEnum.RU))
        english_keys = set(get_i18n_messages(language=LanguageEnum.EN))

        assert english_keys == russian_keys

    def test_all_translatable_enum_values_have_labels(self) -> None:
        for language in LanguageEnum:
            messages = get_i18n_messages(language=language)

            for status in PublishStatusEnum:
                assert f"enum.publishStatus.{status.value}" in messages
            for grade in GradeEnum:
                assert f"enum.grade.{grade.name.title().replace('_', '')}" in messages
            for role in RoleEnum:
                assert f"enum.role.{role.value}" in messages
            for reaction in NoteReactionKind:
                assert f"enum.noteReaction.{reaction.value}" in messages
            for source in NoteViewSourceCategory:
                assert f"enum.noteViewSource.{source.value}" in messages
