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

    def test_admin_panel_navigation_item_labels_omit_repeated_section_domain(self) -> None:
        russian_messages = get_i18n_messages(language=LanguageEnum.RU)
        english_messages = get_i18n_messages(language=LanguageEnum.EN)

        assert russian_messages["adminPanel.section.articleFolders"] == "Папки"
        assert russian_messages["adminPanel.section.articleTags"] == "Теги"
        assert russian_messages["adminPanel.section.matrixQuestions"] == "Вопросы"
        assert russian_messages["adminPanel.section.matrixStructure"] == "Структура"
        assert russian_messages["adminPanel.section.matrixQuestionQueue"] == "Очередь вопросов"
        assert english_messages["adminPanel.section.articleFolders"] == "Folders"
        assert english_messages["adminPanel.section.articleTags"] == "Tags"
        assert english_messages["adminPanel.section.matrixQuestions"] == "Questions"
        assert english_messages["adminPanel.section.matrixStructure"] == "Structure"
        assert english_messages["adminPanel.section.matrixQuestionQueue"] == "Question queue"

    def test_site_build_case_study_catalog_describes_public_engineering_page(self) -> None:
        russian_messages = get_i18n_messages(language=LanguageEnum.RU)
        english_messages = get_i18n_messages(language=LanguageEnum.EN)
        russian_quality_body = russian_messages["siteBuild.quality.body"]
        english_quality_body = english_messages["siteBuild.quality.body"]

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
        assert "самовосстанавливается" in russian_messages["siteBuild.architecture.infraBody"]
        assert "self-recovers" in english_messages["siteBuild.architecture.infraBody"]
        for expected, text in (
            ("SSR", russian_quality_body),
            ("SSR", english_quality_body),
            ("производительность", russian_quality_body),
            ("performance", english_quality_body),
            ("security", english_quality_body),
            ("безопасность", russian_quality_body),
            ("SQL-планы", russian_quality_body),
            ("SQL plans", english_quality_body),
            ("blue/green", russian_quality_body),
            ("blue/green", english_quality_body),
        ):
            assert expected in text
        assert "наблюдаемостью" in russian_messages["siteBuild.next.body"]
        assert "observability" in english_messages["siteBuild.next.body"]
        assert "release process" in russian_messages["siteBuild.decision.deployManifest"]
        assert "controlled release process" in english_messages["siteBuild.decision.deployManifest"]
        assert "runtime-конфигурация" in russian_messages["siteBuild.decision.deployManifest"]
        assert "собирается из manifest" in russian_messages["siteBuild.decision.deployManifest"]
        assert "runtime configuration" in english_messages["siteBuild.decision.deployManifest"]
        assert "from a manifest" in english_messages["siteBuild.decision.deployManifest"]
        assert "ручное подтверждение" in russian_messages["siteBuild.decision.deployManifest"]
        assert "manual approval" in english_messages["siteBuild.decision.deployManifest"]
        assert "blue/green" in russian_messages["siteBuild.decision.deployManifest"]
        assert "blue/green" in english_messages["siteBuild.decision.deployManifest"]
        for stale_text, text in (
            ("static gates", english_quality_body),
            ("own side", english_quality_body),
            ("guardrails", english_quality_body),
            ("guardrails", russian_quality_body),
            ("production-facing", russian_quality_body),
            ("production-facing", english_quality_body),
            ("слепых зон", russian_quality_body),
            ("blind spots", english_quality_body),
            ("server-side session cookie", english_quality_body),
            ("raw user agents", english_quality_body),
            ("Dockerfile lint", english_quality_body),
            ("Trivy config scan", english_quality_body),
            ("per-image Docker build/image scans", english_quality_body),
            ("shared CI graph", english_quality_body),
            ("SSR/Lighthouse", english_quality_body),
            ("SSR/Lighthouse", russian_quality_body),
            ("performance budgets", english_quality_body),
        ):
            assert stale_text not in text
        assert "performance budgets" not in english_messages["siteBuild.next.body"]
        assert "changelog" not in english_messages["siteBuild.next.body"].lower()
        assert "changelog" not in russian_messages["siteBuild.next.body"].lower()

    def test_updates_catalog_describes_public_updates_page(self) -> None:
        russian_messages = get_i18n_messages(language=LanguageEnum.RU)
        english_messages = get_i18n_messages(language=LanguageEnum.EN)

        assert russian_messages["shell.footer.updates"] == "Обновления"
        assert english_messages["shell.footer.updates"] == "Updates"
        assert "публичный журнал" in russian_messages["updates.seo.description"].lower()
        assert "public changelog" in english_messages["updates.seo.description"].lower()
        assert "Major changes" in english_messages["updates.hero.lead"]
        assert "месяцам" in russian_messages["updates.hero.lead"]
        assert russian_messages["updates.tag.backend"] == "Backend"
        assert english_messages["updates.tag.backend"] == "Backend"
        assert russian_messages["updates.tag.delivery"] == "Доставка"
        assert english_messages["updates.tag.delivery"] == "Delivery"
        assert not any(key.startswith("updates.month.") for key in russian_messages)
        assert not any(key.startswith("updates.month.") for key in english_messages)
        assert not any(key.startswith("updates.entry.") for key in russian_messages)
        assert not any(key.startswith("updates.entry.") for key in english_messages)
        assert "выдум" not in russian_messages["updates.hero.lead"].lower()
        assert "точност" not in russian_messages["updates.hero.lead"].lower()
