from core.articles.enums import ArticleReactionKind, ArticleViewSourceCategory
from core.auth.enums import RoleEnum
from core.competency_matrix.enums import GradeEnum, InterviewFrequencyEnum
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
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
            for frequency in InterviewFrequencyEnum:
                assert f"enum.interviewFrequency.{frequency.value}" in messages
            for role in RoleEnum:
                assert f"enum.role.{role.value}" in messages
            for reaction in ArticleReactionKind:
                assert f"enum.articleReaction.{reaction.value}" in messages
            for source in ArticleViewSourceCategory:
                assert f"enum.articleViewSource.{source.value}" in messages

    def test_date_picker_catalog_has_month_year_navigation_labels(self) -> None:
        russian_messages = get_i18n_messages(language=LanguageEnum.RU)
        english_messages = get_i18n_messages(language=LanguageEnum.EN)

        assert russian_messages["shared.datePicker.openMonthYearPicker"] == "Выбрать месяц и год"
        assert russian_messages["shared.datePicker.previousYear"] == "Предыдущий год"
        assert russian_messages["shared.datePicker.nextYear"] == "Следующий год"
        assert english_messages["shared.datePicker.openMonthYearPicker"] == "Choose month and year"
        assert english_messages["shared.datePicker.previousYear"] == "Previous year"
        assert english_messages["shared.datePicker.nextYear"] == "Next year"

    def test_shell_catalog_keeps_footer_contact_without_about_navigation(self) -> None:
        russian_messages = get_i18n_messages(language=LanguageEnum.RU)
        english_messages = get_i18n_messages(language=LanguageEnum.EN)

        assert "shell.nav.about" not in russian_messages
        assert "shell.nav.about" not in english_messages
        assert not any(key.startswith("about.") for key in russian_messages)
        assert not any(key.startswith("about.") for key in english_messages)
        assert russian_messages["shell.footer.email"] == "Эл. почта"
        assert english_messages["shell.footer.email"] == "Email"

    def test_site_build_case_study_catalog_describes_public_engineering_page(self) -> None:
        russian_messages = get_i18n_messages(language=LanguageEnum.RU)
        english_messages = get_i18n_messages(language=LanguageEnum.EN)

        assert russian_messages["shell.footer.siteBuild"] == "Как устроен сайт"
        assert english_messages["shell.footer.siteBuild"] == "How this site is built"
        assert "инженерный разбор" in russian_messages["siteBuild.hero.lead"].lower()
        assert "engineering case study" in english_messages["siteBuild.hero.lead"].lower()
        assert "портфолио" not in russian_messages["siteBuild.hero.lead"].lower()
        assert "личн" not in russian_messages["siteBuild.seo.description"].lower()
        assert "portfolio" not in english_messages["siteBuild.hero.lead"].lower()
        assert "personal" not in english_messages["siteBuild.seo.description"].lower()
        assert "Litestar" in russian_messages["siteBuild.architecture.backendBody"]
        assert "Angular" in english_messages["siteBuild.architecture.frontendBody"]
        assert "Lighthouse CI" in russian_messages["siteBuild.quality.body"]
        assert "Lighthouse CI" in english_messages["siteBuild.quality.body"]
        assert "manual production approval" in russian_messages["siteBuild.decision.deployManifest"]
        assert "manual production approval" in english_messages["siteBuild.decision.deployManifest"]
        assert "static gates" in english_messages["siteBuild.quality.body"]
        assert "static gates" in russian_messages["siteBuild.quality.body"]
        assert "query-plan smoke" in english_messages["siteBuild.quality.body"]
        assert "query-plan smoke" in russian_messages["siteBuild.quality.body"]
        assert "manual environment approval" in english_messages["siteBuild.quality.body"]
        assert "manual environment approval" in russian_messages["siteBuild.quality.body"]
        assert "гейты качества и производительности" in russian_messages["siteBuild.quality.body"]
        assert "quality and performance gates" in english_messages["siteBuild.quality.body"]
        assert "performance budgets" not in english_messages["siteBuild.quality.body"]
        assert "performance budgets" not in english_messages["siteBuild.next.body"]
