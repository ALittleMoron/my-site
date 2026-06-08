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

    def test_date_picker_catalog_has_month_year_navigation_labels(self) -> None:
        russian_messages = get_i18n_messages(language=LanguageEnum.RU)
        english_messages = get_i18n_messages(language=LanguageEnum.EN)

        assert russian_messages["notes.datePicker.openMonthYearPicker"] == "Выбрать месяц и год"
        assert russian_messages["notes.datePicker.previousYear"] == "Предыдущий год"
        assert russian_messages["notes.datePicker.nextYear"] == "Следующий год"
        assert english_messages["notes.datePicker.openMonthYearPicker"] == "Choose month and year"
        assert english_messages["notes.datePicker.previousYear"] == "Previous year"
        assert english_messages["notes.datePicker.nextYear"] == "Next year"

    def test_about_catalog_matches_current_resume_experience(self) -> None:
        russian_messages = get_i18n_messages(language=LanguageEnum.RU)
        english_messages = get_i18n_messages(language=LanguageEnum.EN)

        assert "более чем 6 годами опыта" in russian_messages["about.hero.description"]
        assert "более чем 6 годами опыта" in russian_messages["about.experience.description"]
        assert "more than 6 years of experience" in english_messages["about.hero.description"]
        assert "more than 6 years of experience" in english_messages["about.experience.description"]
        assert russian_messages["about.job.seniorBackendDeveloper"] == "Старший backend-разработчик"
        assert english_messages["about.job.seniorBackendDeveloper"] == "Senior backend developer"
        assert (
            russian_messages["about.job.seniorBackendPythonTechLead"]
            == "Старший backend-разработчик / технический руководитель Python"
        )
        assert (
            english_messages["about.job.seniorBackendPythonTechLead"]
            == "Senior backend developer / Python Tech Lead"
        )
