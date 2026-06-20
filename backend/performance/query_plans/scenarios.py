from collections.abc import Awaitable, Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from hashlib import md5
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.articles.enums import ArticleReactionKind, ArticleViewSourceCategory
from core.articles.schemas import Article, ArticleFilters, ArticleMetadata, Tag, Tags
from core.competency_matrix.enums import CompetencyMatrixWorkspaceSortEnum, GradeEnum
from core.competency_matrix.schemas import (
    AttachedExternalResource,
    AttachedExternalResources,
    CompetencyMatrixItem,
    CompetencyMatrixItemFilters,
    CompetencyMatrixWorkspaceFilters,
    QueuedCompetencyMatrixQuestionCreateParams,
    QueuedCompetencyMatrixQuestionsCreateParams,
)
from core.contacts.schemas import ContactMe
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.resumes.schemas import (
    Resume,
    ResumeContent,
    ResumeCreateParams,
    ResumeFilters,
    ResumeProfile,
    ResumeSummary,
)
from core.types import IntId
from infra.postgresql.storages.articles import (
    ArticleAnalyticsDatabaseStorage,
    ArticlesDatabaseStorage,
)
from infra.postgresql.storages.auth import AuthDatabaseStorage
from infra.postgresql.storages.competency_matrix import CompetencyMatrixDatabaseStorage
from infra.postgresql.storages.contacts import ContactMeDatabaseStorage
from infra.postgresql.storages.resumes import ResumesDatabaseStorage
from infra.postgresql.storages.users import UserAccountDatabaseStorage
from performance.query_plans.expectations import (
    BALANCED_THRESHOLD_POLICY,
    QueryThresholdPolicy,
    scenario_plan_expectation,
)
from performance.query_plans.models import (
    CoverageReport,
    PlanExpectation,
    QueryThresholdGroup,
    StorageMethod,
)

ScenarioRunner = Callable[[AsyncSession], Awaitable[None]]

SEED_NOW = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
SEED_USERNAME = "benchmark"
NEW_AUTH_HASH = "query-plan-auth-hash"
NEW_ARTICLE_ID = UUID("10000000-0000-4000-8000-000000000001")
NEW_CONTACT_ID = UUID("10000000-0000-4000-8000-000000000002")
NEW_ARTICLE_ANALYTICS_VOTER = "query-plan-voter-hash"
NEW_TAG_ID = IntId(90_000_001)
NEW_MATRIX_ITEM_ID = IntId(900_001)
NEW_RESUME_TITLE = "Query plan new resume"
SHORT_TRIGRAM_ALLOW_REASON = (
    "short search string has too few extractable trigrams for an index-selective search"
)


@dataclass(frozen=True, slots=True)
class StorageScenario:
    name: str
    storage_class: str
    method_name: str
    group: QueryThresholdGroup
    expected_index_names: tuple[str, ...]
    forbidden_seq_scan_relations: tuple[str, ...]
    allow_seq_scan_reason: str | None
    run: ScenarioRunner

    def plan_expectation(
        self,
        *,
        policy: QueryThresholdPolicy,
        query_name: str | None,
    ) -> PlanExpectation:
        return scenario_plan_expectation(
            scenario_name=self.name,
            group=self.group,
            policy=policy,
            query_name=query_name,
            expected_index_names=self.expected_index_names,
            forbidden_seq_scan_relations=self.forbidden_seq_scan_relations,
            allow_seq_scan_reason=self.allow_seq_scan_reason,
        )


def evaluate_storage_method_coverage(
    *,
    discovered_methods: Sequence[StorageMethod],
    scenarios: Sequence[StorageScenario],
) -> CoverageReport:
    discovered_by_key = {
        (method.storage_class, method.method_name): method for method in discovered_methods
    }
    scenario_keys = {(scenario.storage_class, scenario.method_name) for scenario in scenarios}
    covered_methods = tuple(
        method
        for method in discovered_methods
        if (method.storage_class, method.method_name) in scenario_keys
    )
    missing_methods = tuple(
        method
        for method in discovered_methods
        if (method.storage_class, method.method_name) not in scenario_keys
    )
    unexpected_methods = tuple(
        StorageMethod(storage_class=storage_class, method_name=method_name, module_name="")
        for storage_class, method_name in sorted(scenario_keys)
        if (storage_class, method_name) not in discovered_by_key
    )
    return CoverageReport(
        discovered_methods=tuple(discovered_methods),
        covered_methods=covered_methods,
        missing_methods=missing_methods,
        unexpected_methods=unexpected_methods,
    )


def coverage_findings(*, coverage: CoverageReport) -> tuple[str, ...]:
    return (
        *(
            f"missing query-plan storage scenario for {method.storage_class}.{method.method_name}"
            for method in coverage.missing_methods
        ),
        *(
            f"query-plan storage scenario references unknown method "
            f"{method.storage_class}.{method.method_name}"
            for method in coverage.unexpected_methods
        ),
    )


async def run_user_get_by_username(session: AsyncSession) -> None:
    await UserAccountDatabaseStorage(session=session).get_user_by_username(SEED_USERNAME)


async def run_update_user_password_hash(session: AsyncSession) -> None:
    await AuthDatabaseStorage(session=session).update_user_password_hash(
        SEED_USERNAME,
        NEW_AUTH_HASH,
    )


async def run_create_contact_me_request(session: AsyncSession) -> None:
    await ContactMeDatabaseStorage(session=session).create_contact_me_request(
        ContactMe(
            id=NEW_CONTACT_ID,
            name="Query Plan",
            email="query-plan@example.test",
            telegram=None,
            message="Please include contact writes in query plan smoke.",
        ),
    )


async def run_list_resumes(session: AsyncSession) -> None:
    await ResumesDatabaseStorage(session=session).list_resumes(
        filters=ResumeFilters(
            page=1,
            page_size=20,
            search_query=None,
            author_username=SEED_USERNAME,
        ),
    )


async def run_get_resume(session: AsyncSession) -> None:
    await ResumesDatabaseStorage(session=session).get_resume(
        resume_id=IntId(100),
        author_username=SEED_USERNAME,
    )


async def run_create_resume(session: AsyncSession) -> None:
    await ResumesDatabaseStorage(session=session).create_resume(
        params=ResumeCreateParams(
            title=NEW_RESUME_TITLE,
            content=write_resume_content(summary_ru="Новое резюме для query-plan smoke."),
            author_username=SEED_USERNAME,
        ),
    )


async def run_update_resume(session: AsyncSession) -> None:
    await ResumesDatabaseStorage(session=session).update_resume(
        resume=Resume(
            id=IntId(100),
            title="Query plan updated resume",
            content=write_resume_content(summary_ru="Обновленное резюме для query-plan smoke."),
            author_username=SEED_USERNAME,
            created_at=SEED_NOW,
            updated_at=SEED_NOW,
        ),
    )


async def run_delete_resume(session: AsyncSession) -> None:
    await ResumesDatabaseStorage(session=session).delete_resume(
        resume_id=IntId(101),
        author_username=SEED_USERNAME,
    )


async def run_get_article_by_slug(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).get_article_by_slug(
        slug="article-100",
        include_deleted_tags=False,
    )


async def run_list_articles_en_full_text_tag_date(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).list_articles(
        filters=ArticleFilters(
            page=1,
            page_size=20,
            language=LanguageEnum.EN,
            only_published=True,
            tag_slug="postgresql",
            published_from=date(2025, 1, 1),
            published_to=date(2026, 5, 31),
            search_query="full text search",
            include_tags=True,
        ),
    )


async def run_list_articles_ru_full_text(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).list_articles(
        filters=ArticleFilters(
            page=1,
            page_size=20,
            language=LanguageEnum.RU,
            only_published=True,
            tag_slug=None,
            published_from=None,
            published_to=None,
            search_query="полнотекстовый поиск",
            include_tags=True,
        ),
    )


async def run_list_articles_for_seo(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).list_articles(
        filters=ArticleFilters(only_published=True, include_tags=False, order_for_seo=True),
    )


async def run_list_tree_items(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).list_tree_items(
        only_published=True,
        language=LanguageEnum.EN,
    )


async def run_create_article(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).create_article(article=write_article())


async def run_update_article(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).update_article(
        article=write_article_for_existing_article(),
    )


async def run_delete_article(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).delete_article(slug="article-101")


async def run_update_article_publish_status(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).update_article_publish_status(
        slug="article-102",
        publish_status=PublishStatusEnum.DRAFT,
    )


async def run_get_tags_by_ids(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).get_tags_by_ids(
        tag_ids=[IntId(1), IntId(2), IntId(3)],
        include_deleted=False,
    )


async def run_list_tags(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).list_tags(
        include_deleted=False,
        language=LanguageEnum.EN,
    )


async def run_search_tags_exact(session: AsyncSession) -> None:
    await run_search_tags(session=session, search_name="python")


async def run_search_tags_substring(session: AsyncSession) -> None:
    await run_search_tags(session=session, search_name="thon")


async def run_search_tags_fuzzy(session: AsyncSession) -> None:
    await run_search_tags(session=session, search_name="pythno")


async def run_search_tags_short(session: AsyncSession) -> None:
    await run_search_tags(session=session, search_name="py")


async def run_search_tags(*, session: AsyncSession, search_name: str) -> None:
    await ArticlesDatabaseStorage(session=session).search_tags(
        search_name=search_name,
        include_deleted=False,
        limit=10,
        language=LanguageEnum.EN,
    )


async def run_create_tag(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).create_tag(
        tag=Tag(
            id=NEW_TAG_ID,
            name_ru="Новый performance тег",
            name_en="New performance tag",
            slug="query-plan-new-tag",
            deleted_at=None,
        ),
    )


async def run_update_tag(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).update_tag(
        tag=Tag(
            id=IntId(1),
            name_ru="Питон обновленный",
            name_en="Python updated",
            slug="python",
            deleted_at=None,
        ),
    )


async def run_soft_delete_tag(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).soft_delete_tag(tag_id=IntId(1))


async def run_restore_tag(session: AsyncSession) -> None:
    await ArticlesDatabaseStorage(session=session).restore_tag(tag_id=IntId(4))


async def run_increment_view(session: AsyncSession) -> None:
    await ArticleAnalyticsDatabaseStorage(session=session).increment_view(
        article_id=article_id(100),
        source_category=ArticleViewSourceCategory.DIRECT,
        viewed_on=SEED_NOW.date(),
    )


async def run_increment_engaged_view(session: AsyncSession) -> None:
    await ArticleAnalyticsDatabaseStorage(session=session).increment_engaged_view(
        article_id=article_id(100),
        source_category=ArticleViewSourceCategory.SEARCH,
        viewed_on=SEED_NOW.date(),
    )


async def run_get_public_stats(session: AsyncSession) -> None:
    await ArticleAnalyticsDatabaseStorage(session=session).get_public_stats(
        article_ids=[article_id(100), article_id(200)],
    )


async def run_get_reaction_counts(session: AsyncSession) -> None:
    await ArticleAnalyticsDatabaseStorage(session=session).get_reaction_counts(
        article_ids=[article_id(100), article_id(200)],
    )


async def run_set_reaction(session: AsyncSession) -> None:
    await ArticleAnalyticsDatabaseStorage(session=session).set_reaction(
        article_id=article_id(100),
        article_scoped_voter_hash=NEW_ARTICLE_ANALYTICS_VOTER,
        reaction_kind=ArticleReactionKind.HEART,
    )


async def run_get_daily_stats(session: AsyncSession) -> None:
    await ArticleAnalyticsDatabaseStorage(session=session).get_daily_stats(
        date_from=date(2026, 1, 1),
        date_to=date(2026, 1, 31),
        language=LanguageEnum.EN,
    )


async def run_list_sheets(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).list_sheets()


async def run_list_competency_matrix_items(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).list_competency_matrix_items(
        filters=CompetencyMatrixItemFilters(sheet_key="python", only_published=True),
    )


async def run_list_competency_matrix_workspace_items(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).list_competency_matrix_workspace_items(
        filters=CompetencyMatrixWorkspaceFilters(
            page=1,
            page_size=20,
            language=LanguageEnum.EN,
            sort=CompetencyMatrixWorkspaceSortEnum.SECTION,
            search_query=None,
            sheet_keys=("python",),
            grades=(GradeEnum.JUNIOR,),
            sections=(),
            subsections=(),
            publish_statuses=(PublishStatusEnum.PUBLISHED,),
            published_from=None,
            published_to=None,
            has_missing_fields=None,
        ),
    )


async def run_list_competency_matrix_workspace_filter_options(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(
        session=session,
    ).list_competency_matrix_workspace_filter_options(language=LanguageEnum.EN)


async def run_get_competency_matrix_item(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).get_competency_matrix_item(IntId(100))


async def run_get_competency_matrix_item_by_slug(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).get_competency_matrix_item_by_slug(
        "matrix-question-100",
    )


async def run_create_competency_matrix_item(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).create_competency_matrix_item(
        write_matrix_item(item_id=NEW_MATRIX_ITEM_ID, slug="query-plan-new-matrix-item"),
    )


async def run_update_competency_matrix_item(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).update_competency_matrix_item(
        write_matrix_item(item_id=IntId(100), slug="matrix-question-100"),
    )


async def run_update_competency_matrix_item_publish_status(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(
        session=session,
    ).update_competency_matrix_item_publish_status(
        IntId(100),
        PublishStatusEnum.DRAFT,
    )


async def run_list_queued_questions(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).list_queued_questions()


async def run_get_queued_question(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).get_queued_question(IntId(100))


async def run_create_queued_question(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).create_queued_question(
        params=QueuedCompetencyMatrixQuestionCreateParams(
            question="How should query-plan checks cover the matrix queue?",
        ),
    )


async def run_create_queued_questions(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).create_queued_questions(
        params=QueuedCompetencyMatrixQuestionsCreateParams(
            questions=[
                QueuedCompetencyMatrixQuestionCreateParams(
                    question="How should query-plan checks cover matrix imports?",
                ),
                QueuedCompetencyMatrixQuestionCreateParams(
                    question="How should FIFO ordering behave for imported questions?",
                ),
            ],
        ),
    )


async def run_delete_queued_question(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).delete_queued_question(IntId(101))


async def run_get_resources_by_ids(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).get_resources_by_ids(
        [IntId(1), IntId(2), IntId(3)],
    )


async def run_delete_competency_matrix_item(session: AsyncSession) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).delete_competency_matrix_item(IntId(101))


async def run_search_resources_exact(session: AsyncSession) -> None:
    await run_search_resources(session=session, search_name="pydantic")


async def run_search_resources_url(session: AsyncSession) -> None:
    await run_search_resources(session=session, search_name="python")


async def run_search_resources_fuzzy(session: AsyncSession) -> None:
    await run_search_resources(session=session, search_name="pydntic")


async def run_search_resources_short(session: AsyncSession) -> None:
    await run_search_resources(session=session, search_name="py")


async def run_search_resources(*, session: AsyncSession, search_name: str) -> None:
    await CompetencyMatrixDatabaseStorage(session=session).search_competency_matrix_resources(
        search_name,
        10,
        LanguageEnum.EN,
    )


def article_id(value: int) -> UUID:
    digest = md5(str(value).encode(), usedforsecurity=False).hexdigest()
    return UUID(
        f"{digest[0:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}",
    )


def write_article() -> Article:
    return Article(
        id=NEW_ARTICLE_ID,
        slug="query-plan-new-article",
        title_ru="Новая статья query plan",
        title_en="New query plan article",
        content_ru="Контент для smoke проверки запросов",
        content_en="Content for query smoke checks",
        folder_ru="Производительность",
        folder_en="Performance",
        author_username=SEED_USERNAME,
        published_at=SEED_NOW,
        publish_status=PublishStatusEnum.PUBLISHED,
        metadata=empty_article_metadata(),
        created_at=SEED_NOW,
        updated_at=SEED_NOW,
        tags=Tags(values=[seed_tag(IntId(1)), seed_tag(IntId(2))]),
    )


def write_article_for_existing_article() -> Article:
    return Article(
        id=article_id(99),
        slug="article-99-updated",
        title_ru="Обновленная статья query plan",
        title_en="Updated query plan article",
        content_ru="Обновленный контент для smoke проверки",
        content_en="Updated content for query smoke checks",
        folder_ru="Производительность",
        folder_en="Performance",
        author_username=SEED_USERNAME,
        published_at=SEED_NOW,
        publish_status=PublishStatusEnum.PUBLISHED,
        metadata=empty_article_metadata(),
        created_at=SEED_NOW,
        updated_at=SEED_NOW,
        tags=Tags(values=[seed_tag(IntId(1)), seed_tag(IntId(2))]),
    )


def empty_article_metadata() -> ArticleMetadata:
    return ArticleMetadata(
        seo_title_ru=None,
        seo_title_en=None,
        seo_description_ru=None,
        seo_description_en=None,
        cover_image_url=None,
        cover_image_alt_ru=None,
        cover_image_alt_en=None,
    )


def seed_tag(tag_id: IntId) -> Tag:
    names = {
        IntId(1): ("Питон", "Python", "python"),
        IntId(2): ("PostgreSQL", "PostgreSQL", "postgresql"),
        IntId(3): ("Pydantic", "Pydantic", "pydantic"),
    }
    name_ru, name_en, slug = names[tag_id]
    return Tag(id=tag_id, name_ru=name_ru, name_en=name_en, slug=slug, deleted_at=None)


def write_resume_content(*, summary_ru: str) -> ResumeContent:
    return ResumeContent(
        profile=ResumeProfile(
            full_name="Query Plan Candidate",
            role_ru="Инженер",
            role_en="Engineer",
            location_ru="",
            location_en="",
            email="",
            phone="",
            website_url="",
            linkedin_url="",
            github_url="",
            telegram="",
        ),
        summary=ResumeSummary(
            text_ru=summary_ru,
            text_en="Resume content for query-plan smoke.",
        ),
        skills=[],
        experience=[],
        education=[],
        languages=[],
        certifications=[],
        additional_sections=[],
    )


def write_matrix_item(*, item_id: IntId, slug: str) -> CompetencyMatrixItem:
    return CompetencyMatrixItem(
        id=item_id,
        slug=slug,
        question_ru="Как smoke проверяет запросы?",
        question_en="How does the smoke check queries?",
        publish_status=PublishStatusEnum.PUBLISHED,
        published_at=SEED_NOW,
        answer_ru="Через deterministic storage сценарии.",
        answer_en="Through deterministic storage scenarios.",
        interview_expected_answer_ru="Назвать listener, EXPLAIN и thresholds.",
        interview_expected_answer_en="Name listener, EXPLAIN, and thresholds.",
        sheet_key="python",
        sheet_ru="Питон",
        sheet_en="Python",
        grade=GradeEnum.JUNIOR,
        section_ru="Основы",
        section_en="Basics",
        subsection_ru="Производительность",
        subsection_en="Performance",
        resources=AttachedExternalResources(
            values=[
                AttachedExternalResource(
                    id=IntId(1),
                    name_ru="Документация Pydantic",
                    name_en="Pydantic validation guide",
                    url="https://docs.pydantic.dev/latest/",
                    context_ru="Контекст для smoke",
                    context_en="Smoke context",
                ),
            ],
        ),
    )


def scenario(  # noqa: PLR0913
    *,
    name: str,
    storage_class: str,
    method_name: str,
    group: QueryThresholdGroup,
    expected_index_names: Iterable[str],
    forbidden_seq_scan_relations: Iterable[str],
    allow_seq_scan_reason: str | None,
    run: ScenarioRunner,
) -> StorageScenario:
    return StorageScenario(
        name=name,
        storage_class=storage_class,
        method_name=method_name,
        group=group,
        expected_index_names=tuple(expected_index_names),
        forbidden_seq_scan_relations=tuple(forbidden_seq_scan_relations),
        allow_seq_scan_reason=allow_seq_scan_reason,
        run=run,
    )


STORAGE_SCENARIOS = (
    scenario(
        name="user_get_by_username",
        storage_class="UserAccountDatabaseStorage",
        method_name="get_user_by_username",
        group=QueryThresholdGroup.POINT_READ,
        expected_index_names=("users_username_idx",),
        forbidden_seq_scan_relations=("auth__user_model",),
        allow_seq_scan_reason=None,
        run=run_user_get_by_username,
    ),
    scenario(
        name="auth_update_user_password_hash",
        storage_class="AuthDatabaseStorage",
        method_name="update_user_password_hash",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=("users_username_idx",),
        forbidden_seq_scan_relations=("auth__user_model",),
        allow_seq_scan_reason=None,
        run=run_update_user_password_hash,
    ),
    scenario(
        name="contact_create_request",
        storage_class="ContactMeDatabaseStorage",
        method_name="create_contact_me_request",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_create_contact_me_request,
    ),
    scenario(
        name="resumes_list_workspace",
        storage_class="ResumesDatabaseStorage",
        method_name="list_resumes",
        group=QueryThresholdGroup.LIST_READ,
        expected_index_names=("resumes_resume_author_updated_id_idx",),
        forbidden_seq_scan_relations=("resumes__resume_model",),
        allow_seq_scan_reason="list_resumes includes an exact private workspace count query",
        run=run_list_resumes,
    ),
    scenario(
        name="resumes_detail_by_id",
        storage_class="ResumesDatabaseStorage",
        method_name="get_resume",
        group=QueryThresholdGroup.POINT_READ,
        expected_index_names=("resumes__resume_model_pkey",),
        forbidden_seq_scan_relations=("resumes__resume_model",),
        allow_seq_scan_reason=None,
        run=run_get_resume,
    ),
    scenario(
        name="resumes_create",
        storage_class="ResumesDatabaseStorage",
        method_name="create_resume",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_create_resume,
    ),
    scenario(
        name="resumes_update",
        storage_class="ResumesDatabaseStorage",
        method_name="update_resume",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=("resumes__resume_model_pkey",),
        forbidden_seq_scan_relations=("resumes__resume_model",),
        allow_seq_scan_reason=None,
        run=run_update_resume,
    ),
    scenario(
        name="resumes_delete",
        storage_class="ResumesDatabaseStorage",
        method_name="delete_resume",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=("resumes__resume_model_pkey",),
        forbidden_seq_scan_relations=("resumes__resume_model",),
        allow_seq_scan_reason=None,
        run=run_delete_resume,
    ),
    scenario(
        name="articles_detail_by_slug",
        storage_class="ArticlesDatabaseStorage",
        method_name="get_article_by_slug",
        group=QueryThresholdGroup.POINT_READ,
        expected_index_names=(),
        forbidden_seq_scan_relations=("articles__article_model",),
        allow_seq_scan_reason=None,
        run=run_get_article_by_slug,
    ),
    scenario(
        name="articles_list_en_full_text_tag_date",
        storage_class="ArticlesDatabaseStorage",
        method_name="list_articles",
        group=QueryThresholdGroup.SEARCH,
        expected_index_names=(),
        forbidden_seq_scan_relations=(
            "articles__article_model",
            "articles__article_to_tag_secondary_model",
        ),
        allow_seq_scan_reason=None,
        run=run_list_articles_en_full_text_tag_date,
    ),
    scenario(
        name="articles_list_ru_full_text",
        storage_class="ArticlesDatabaseStorage",
        method_name="list_articles",
        group=QueryThresholdGroup.SEARCH,
        expected_index_names=(),
        forbidden_seq_scan_relations=("articles__article_model",),
        allow_seq_scan_reason=None,
        run=run_list_articles_ru_full_text,
    ),
    scenario(
        name="articles_published_for_seo_sitemap",
        storage_class="ArticlesDatabaseStorage",
        method_name="list_articles",
        group=QueryThresholdGroup.LIST_READ,
        expected_index_names=("articles_article_publish_status_published_updated_idx",),
        forbidden_seq_scan_relations=("articles__article_model",),
        allow_seq_scan_reason=None,
        run=run_list_articles_for_seo,
    ),
    scenario(
        name="articles_tree_published",
        storage_class="ArticlesDatabaseStorage",
        method_name="list_tree_items",
        group=QueryThresholdGroup.HEAVY,
        expected_index_names=("articles_article_tree_en_published_idx",),
        forbidden_seq_scan_relations=("articles__article_model",),
        allow_seq_scan_reason=None,
        run=run_list_tree_items,
    ),
    scenario(
        name="articles_create",
        storage_class="ArticlesDatabaseStorage",
        method_name="create_article",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=("articles__article_model",),
        allow_seq_scan_reason=None,
        run=run_create_article,
    ),
    scenario(
        name="articles_update",
        storage_class="ArticlesDatabaseStorage",
        method_name="update_article",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=("articles__article_model",),
        allow_seq_scan_reason=None,
        run=run_update_article,
    ),
    scenario(
        name="articles_delete",
        storage_class="ArticlesDatabaseStorage",
        method_name="delete_article",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=("articles__article_model",),
        allow_seq_scan_reason=None,
        run=run_delete_article,
    ),
    scenario(
        name="articles_update_publish_status",
        storage_class="ArticlesDatabaseStorage",
        method_name="update_article_publish_status",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=("articles__article_model",),
        allow_seq_scan_reason=None,
        run=run_update_article_publish_status,
    ),
    scenario(
        name="tags_get_by_ids",
        storage_class="ArticlesDatabaseStorage",
        method_name="get_tags_by_ids",
        group=QueryThresholdGroup.POINT_READ,
        expected_index_names=("articles__tag_model_pkey",),
        forbidden_seq_scan_relations=("articles__tag_model",),
        allow_seq_scan_reason=None,
        run=run_get_tags_by_ids,
    ),
    scenario(
        name="tags_list",
        storage_class="ArticlesDatabaseStorage",
        method_name="list_tags",
        group=QueryThresholdGroup.LIST_READ,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason="full tag listing is intentionally sorted for authoring UI",
        run=run_list_tags,
    ),
    *(
        scenario(
            name=name,
            storage_class="ArticlesDatabaseStorage",
            method_name="search_tags",
            group=QueryThresholdGroup.SEARCH,
            expected_index_names=indexes,
            forbidden_seq_scan_relations=forbidden_relations,
            allow_seq_scan_reason=allow_reason,
            run=runner,
        )
        for name, runner, indexes, forbidden_relations, allow_reason in (
            (
                "tags_exact_en",
                run_search_tags_exact,
                (
                    "articles_tag_name_en_trgm_idx",
                    "articles_tag_name_ru_trgm_idx",
                    "articles_tag_slug_trgm_idx",
                ),
                ("articles__tag_model",),
                None,
            ),
            (
                "tags_substring_en",
                run_search_tags_substring,
                (
                    "articles_tag_name_en_trgm_idx",
                    "articles_tag_name_ru_trgm_idx",
                    "articles_tag_slug_trgm_idx",
                ),
                ("articles__tag_model",),
                None,
            ),
            (
                "tags_fuzzy_en",
                run_search_tags_fuzzy,
                (
                    "articles_tag_name_en_trgm_idx",
                    "articles_tag_name_ru_trgm_idx",
                    "articles_tag_slug_trgm_idx",
                ),
                ("articles__tag_model",),
                None,
            ),
            (
                "tags_short_en",
                run_search_tags_short,
                (),
                (),
                SHORT_TRIGRAM_ALLOW_REASON,
            ),
        )
    ),
    scenario(
        name="tags_create",
        storage_class="ArticlesDatabaseStorage",
        method_name="create_tag",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_create_tag,
    ),
    scenario(
        name="tags_update",
        storage_class="ArticlesDatabaseStorage",
        method_name="update_tag",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=("articles__tag_model_pkey",),
        forbidden_seq_scan_relations=("articles__tag_model",),
        allow_seq_scan_reason=None,
        run=run_update_tag,
    ),
    scenario(
        name="tags_soft_delete",
        storage_class="ArticlesDatabaseStorage",
        method_name="soft_delete_tag",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=("articles__tag_model_pkey",),
        forbidden_seq_scan_relations=("articles__tag_model",),
        allow_seq_scan_reason=None,
        run=run_soft_delete_tag,
    ),
    scenario(
        name="tags_restore",
        storage_class="ArticlesDatabaseStorage",
        method_name="restore_tag",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=("articles__tag_model_pkey",),
        forbidden_seq_scan_relations=("articles__tag_model",),
        allow_seq_scan_reason=None,
        run=run_restore_tag,
    ),
    scenario(
        name="article_analytics_increment_view",
        storage_class="ArticleAnalyticsDatabaseStorage",
        method_name="increment_view",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_increment_view,
    ),
    scenario(
        name="article_analytics_increment_engaged_view",
        storage_class="ArticleAnalyticsDatabaseStorage",
        method_name="increment_engaged_view",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_increment_engaged_view,
    ),
    scenario(
        name="article_analytics_public_stats",
        storage_class="ArticleAnalyticsDatabaseStorage",
        method_name="get_public_stats",
        group=QueryThresholdGroup.AGGREGATE,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_get_public_stats,
    ),
    scenario(
        name="article_analytics_reaction_counts",
        storage_class="ArticleAnalyticsDatabaseStorage",
        method_name="get_reaction_counts",
        group=QueryThresholdGroup.AGGREGATE,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_get_reaction_counts,
    ),
    scenario(
        name="article_analytics_set_reaction",
        storage_class="ArticleAnalyticsDatabaseStorage",
        method_name="set_reaction",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=("articles__article_reaction_model",),
        allow_seq_scan_reason=None,
        run=run_set_reaction,
    ),
    scenario(
        name="article_analytics_daily_stats",
        storage_class="ArticleAnalyticsDatabaseStorage",
        method_name="get_daily_stats",
        group=QueryThresholdGroup.AGGREGATE,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_get_daily_stats,
    ),
    scenario(
        name="matrix_list_sheets",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="list_sheets",
        group=QueryThresholdGroup.LIST_READ,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_list_sheets,
    ),
    scenario(
        name="matrix_list_items",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="list_competency_matrix_items",
        group=QueryThresholdGroup.HEAVY,
        expected_index_names=("cmi_sheet_key_status_order_idx",),
        forbidden_seq_scan_relations=("competency_matrix__competency_matrix_item_model",),
        allow_seq_scan_reason=None,
        run=run_list_competency_matrix_items,
    ),
    scenario(
        name="matrix_workspace_list_items",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="list_competency_matrix_workspace_items",
        group=QueryThresholdGroup.HEAVY,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_list_competency_matrix_workspace_items,
    ),
    scenario(
        name="matrix_workspace_filter_options",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="list_competency_matrix_workspace_filter_options",
        group=QueryThresholdGroup.HEAVY,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_list_competency_matrix_workspace_filter_options,
    ),
    scenario(
        name="matrix_detail_by_id",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="get_competency_matrix_item",
        group=QueryThresholdGroup.POINT_READ,
        expected_index_names=(),
        forbidden_seq_scan_relations=("competency_matrix__competency_matrix_item_model",),
        allow_seq_scan_reason=None,
        run=run_get_competency_matrix_item,
    ),
    scenario(
        name="matrix_public_detail_by_slug",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="get_competency_matrix_item_by_slug",
        group=QueryThresholdGroup.POINT_READ,
        expected_index_names=(),
        forbidden_seq_scan_relations=("competency_matrix__competency_matrix_item_model",),
        allow_seq_scan_reason=None,
        run=run_get_competency_matrix_item_by_slug,
    ),
    scenario(
        name="matrix_create_item",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="create_competency_matrix_item",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=("competency_matrix__competency_matrix_item_model",),
        allow_seq_scan_reason=None,
        run=run_create_competency_matrix_item,
    ),
    scenario(
        name="matrix_update_item",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="update_competency_matrix_item",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=("competency_matrix__competency_matrix_item_model",),
        allow_seq_scan_reason=None,
        run=run_update_competency_matrix_item,
    ),
    scenario(
        name="matrix_update_publish_status",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="update_competency_matrix_item_publish_status",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=("competency_matrix__competency_matrix_item_model",),
        allow_seq_scan_reason=None,
        run=run_update_competency_matrix_item_publish_status,
    ),
    scenario(
        name="matrix_queue_list_fifo",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="list_queued_questions",
        group=QueryThresholdGroup.LIST_READ,
        expected_index_names=("cm_queued_question_fifo_idx",),
        forbidden_seq_scan_relations=("competency_matrix__queued_question_model",),
        allow_seq_scan_reason=None,
        run=run_list_queued_questions,
    ),
    scenario(
        name="matrix_queue_detail_by_id",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="get_queued_question",
        group=QueryThresholdGroup.POINT_READ,
        expected_index_names=("competency_matrix__queued_question_model_pkey",),
        forbidden_seq_scan_relations=("competency_matrix__queued_question_model",),
        allow_seq_scan_reason=None,
        run=run_get_queued_question,
    ),
    scenario(
        name="matrix_queue_create",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="create_queued_question",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_create_queued_question,
    ),
    scenario(
        name="matrix_queue_batch_create",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="create_queued_questions",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=(),
        allow_seq_scan_reason=None,
        run=run_create_queued_questions,
    ),
    scenario(
        name="matrix_queue_delete",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="delete_queued_question",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=("competency_matrix__queued_question_model_pkey",),
        forbidden_seq_scan_relations=("competency_matrix__queued_question_model",),
        allow_seq_scan_reason=None,
        run=run_delete_queued_question,
    ),
    scenario(
        name="matrix_resources_by_ids",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="get_resources_by_ids",
        group=QueryThresholdGroup.POINT_READ,
        expected_index_names=("competency_matrix__external_resource_model_pkey",),
        forbidden_seq_scan_relations=("competency_matrix__external_resource_model",),
        allow_seq_scan_reason=None,
        run=run_get_resources_by_ids,
    ),
    scenario(
        name="matrix_delete_item",
        storage_class="CompetencyMatrixDatabaseStorage",
        method_name="delete_competency_matrix_item",
        group=QueryThresholdGroup.SMALL_WRITE,
        expected_index_names=(),
        forbidden_seq_scan_relations=("competency_matrix__competency_matrix_item_model",),
        allow_seq_scan_reason=None,
        run=run_delete_competency_matrix_item,
    ),
    *(
        scenario(
            name=name,
            storage_class="CompetencyMatrixDatabaseStorage",
            method_name="search_competency_matrix_resources",
            group=QueryThresholdGroup.SEARCH,
            expected_index_names=indexes,
            forbidden_seq_scan_relations=forbidden_relations,
            allow_seq_scan_reason=allow_reason,
            run=runner,
        )
        for name, runner, indexes, forbidden_relations, allow_reason in (
            (
                "resources_exact_en",
                run_search_resources_exact,
                (
                    "cm_external_resource_name_en_trgm_idx",
                    "cm_external_resource_name_ru_trgm_idx",
                    "cm_external_resource_url_trgm_idx",
                ),
                ("competency_matrix__external_resource_model",),
                None,
            ),
            (
                "resources_url_en",
                run_search_resources_url,
                (
                    "cm_external_resource_name_en_trgm_idx",
                    "cm_external_resource_name_ru_trgm_idx",
                    "cm_external_resource_url_trgm_idx",
                ),
                ("competency_matrix__external_resource_model",),
                None,
            ),
            (
                "resources_fuzzy_en",
                run_search_resources_fuzzy,
                (
                    "cm_external_resource_name_en_trgm_idx",
                    "cm_external_resource_name_ru_trgm_idx",
                    "cm_external_resource_url_trgm_idx",
                ),
                ("competency_matrix__external_resource_model",),
                None,
            ),
            (
                "resources_short_en",
                run_search_resources_short,
                (),
                (),
                SHORT_TRIGRAM_ALLOW_REASON,
            ),
        )
    ),
)


def scenario_expectation_map(
    *,
    scenarios: Sequence[StorageScenario],
    policy: QueryThresholdPolicy,
) -> dict[str, PlanExpectation]:
    return {
        scenario.name: scenario.plan_expectation(policy=policy, query_name=None)
        for scenario in scenarios
    }


BALANCED_SCENARIO_EXPECTATIONS = scenario_expectation_map(
    scenarios=STORAGE_SCENARIOS,
    policy=BALANCED_THRESHOLD_POLICY,
)
