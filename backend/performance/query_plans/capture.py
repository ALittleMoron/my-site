from collections.abc import Iterator
from datetime import date
from typing import cast

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.i18n.enums import LanguageEnum
from core.notes.schemas import NoteFilters
from infra.postgresql.storages.competency_matrix import CompetencyMatrixDatabaseStorage
from infra.postgresql.storages.notes import NotesDatabaseStorage
from performance.query_plans.models import CapturedQuery, PlanExpectation


class EmptyScalarResult:
    def unique(self) -> EmptyScalarResult:
        return self

    def __iter__(self) -> Iterator[object]:
        return iter(())


class EmptyRowResult:
    def __iter__(self) -> Iterator[tuple[object, ...]]:
        return iter(())


class FakeScalarModel:
    def to_domain_schema(self, *, include_relationships: bool) -> object:
        del include_relationships
        return object()


class RecordingSession:
    def __init__(self, *, scalar_result: object = 0) -> None:
        self.scalar_result = scalar_result
        self.execute_statements: list[Select[tuple[object, ...]]] = []
        self.scalar_statements: list[Select[tuple[object, ...]]] = []
        self.scalars_statements: list[Select[tuple[object, ...]]] = []

    async def execute(self, statement: Select[tuple[object, ...]]) -> EmptyRowResult:
        self.execute_statements.append(statement)
        return EmptyRowResult()

    async def scalar(self, statement: Select[tuple[object, ...]]) -> object:
        self.scalar_statements.append(statement)
        return self.scalar_result

    async def scalars(self, statement: Select[tuple[object, ...]]) -> EmptyScalarResult:
        self.scalars_statements.append(statement)
        return EmptyScalarResult()


async def capture_balanced_queries() -> tuple[CapturedQuery, ...]:
    notes_with_tag_session = RecordingSession()
    notes_with_tag_storage = NotesDatabaseStorage(
        session=cast("AsyncSession", notes_with_tag_session),
    )
    await notes_with_tag_storage.list_notes(
        filters=NoteFilters(
            page=1,
            page_size=20,
            language=LanguageEnum.EN,
            only_published=True,
            tag_slug="postgresql",
            published_from=date(2025, 1, 1),
            published_to=date(2026, 5, 31),
            search_query="full text search",
        ),
    )

    notes_ru_session = RecordingSession()
    notes_ru_storage = NotesDatabaseStorage(session=cast("AsyncSession", notes_ru_session))
    await notes_ru_storage.list_notes(
        filters=NoteFilters(
            page=1,
            page_size=20,
            language=LanguageEnum.RU,
            only_published=True,
            tag_slug=None,
            published_from=None,
            published_to=None,
            search_query="полнотекстовый поиск",
        ),
    )

    notes_seo_session = RecordingSession()
    notes_seo_storage = NotesDatabaseStorage(session=cast("AsyncSession", notes_seo_session))
    await notes_seo_storage.list_published_notes_for_seo()

    matrix_slug_session = RecordingSession(scalar_result=FakeScalarModel())
    matrix_slug_storage = CompetencyMatrixDatabaseStorage(
        session=cast("AsyncSession", matrix_slug_session),
    )
    await matrix_slug_storage.get_competency_matrix_item_by_slug(slug="matrix-question-100")

    tag_queries = await _capture_tag_queries()
    resource_queries = await _capture_resource_queries()

    return (
        CapturedQuery(
            name="notes_list_en_full_text_tag_date",
            statement=notes_with_tag_session.scalars_statements[0],
            expectation=PlanExpectation(
                max_execution_ms=150.0,
                expected_index_names=("notes_note_search_vector_en_gin_idx",),
                forbidden_seq_scan_relations=(
                    "notes__note_model",
                    "notes__note_to_tag_secondary_model",
                ),
                allow_seq_scan_reason=None,
            ),
        ),
        CapturedQuery(
            name="notes_count_en_full_text_tag_date",
            statement=notes_with_tag_session.scalar_statements[0],
            expectation=PlanExpectation(
                max_execution_ms=250.0,
                expected_index_names=("notes_note_search_vector_en_gin_idx",),
                forbidden_seq_scan_relations=(
                    "notes__note_model",
                    "notes__note_to_tag_secondary_model",
                ),
                allow_seq_scan_reason=None,
            ),
        ),
        CapturedQuery(
            name="notes_list_ru_full_text",
            statement=notes_ru_session.scalars_statements[0],
            expectation=PlanExpectation(
                max_execution_ms=150.0,
                expected_index_names=("notes_note_search_vector_gin_idx",),
                forbidden_seq_scan_relations=("notes__note_model",),
                allow_seq_scan_reason=None,
            ),
        ),
        CapturedQuery(
            name="notes_count_ru_full_text",
            statement=notes_ru_session.scalar_statements[0],
            expectation=PlanExpectation(
                max_execution_ms=250.0,
                expected_index_names=("notes_note_search_vector_gin_idx",),
                forbidden_seq_scan_relations=("notes__note_model",),
                allow_seq_scan_reason=None,
            ),
        ),
        CapturedQuery(
            name="notes_published_for_seo_sitemap",
            statement=notes_seo_session.execute_statements[0],
            expectation=PlanExpectation(
                max_execution_ms=250.0,
                expected_index_names=("notes_note_publish_status_published_updated_idx",),
                forbidden_seq_scan_relations=("notes__note_model",),
                allow_seq_scan_reason=None,
            ),
        ),
        CapturedQuery(
            name="matrix_public_detail_by_slug",
            statement=matrix_slug_session.scalar_statements[0],
            expectation=PlanExpectation(
                max_execution_ms=25.0,
                expected_index_names=("ix_competency_matrix__competency_matrix_item_model_slug",),
                forbidden_seq_scan_relations=("competency_matrix__competency_matrix_item_model",),
                allow_seq_scan_reason=None,
            ),
        ),
        *tag_queries,
        *resource_queries,
    )


async def _capture_tag_queries() -> tuple[CapturedQuery, ...]:
    exact_query = await _capture_tag_query(name="tags_exact_en", search_name="python")
    substring_query = await _capture_tag_query(name="tags_substring_en", search_name="thon")
    fuzzy_query = await _capture_tag_query(name="tags_fuzzy_en", search_name="pythno")
    short_query = await _capture_tag_query(name="tags_short_en", search_name="py")
    return (
        exact_query,
        substring_query,
        fuzzy_query,
        CapturedQuery(
            name=short_query.name,
            statement=short_query.statement,
            expectation=PlanExpectation(
                max_execution_ms=250.0,
                expected_index_names=(),
                forbidden_seq_scan_relations=(),
                allow_seq_scan_reason=(
                    "short search string has too few extractable trigrams for an index-selective "
                    "pg_trgm search"
                ),
            ),
        ),
    )


async def _capture_tag_query(*, name: str, search_name: str) -> CapturedQuery:
    session = RecordingSession()
    storage = NotesDatabaseStorage(session=cast("AsyncSession", session))
    await storage.search_tags(
        search_name=search_name,
        include_deleted=False,
        limit=10,
        language=LanguageEnum.EN,
    )
    return CapturedQuery(
        name=name,
        statement=session.scalars_statements[0],
        expectation=PlanExpectation(
            max_execution_ms=100.0,
            expected_index_names=(
                "notes_tag_name_en_trgm_idx",
                "notes_tag_name_ru_trgm_idx",
                "notes_tag_slug_trgm_idx",
            ),
            forbidden_seq_scan_relations=("notes__tag_model",),
            allow_seq_scan_reason=None,
        ),
    )


async def _capture_resource_queries() -> tuple[CapturedQuery, ...]:
    exact_query = await _capture_resource_query(name="resources_exact_en", search_name="pydantic")
    substring_query = await _capture_resource_query(name="resources_url_en", search_name="pydantic")
    fuzzy_query = await _capture_resource_query(name="resources_fuzzy_en", search_name="pydntic")
    short_query = await _capture_resource_query(name="resources_short_en", search_name="py")
    return (
        exact_query,
        substring_query,
        fuzzy_query,
        CapturedQuery(
            name=short_query.name,
            statement=short_query.statement,
            expectation=PlanExpectation(
                max_execution_ms=250.0,
                expected_index_names=(),
                forbidden_seq_scan_relations=(),
                allow_seq_scan_reason=(
                    "short search string has too few extractable trigrams for an index-selective "
                    "pg_trgm search"
                ),
            ),
        ),
    )


async def _capture_resource_query(*, name: str, search_name: str) -> CapturedQuery:
    session = RecordingSession()
    storage = CompetencyMatrixDatabaseStorage(session=cast("AsyncSession", session))
    await storage.search_competency_matrix_resources(
        search_name=search_name,
        limit=10,
        language=LanguageEnum.EN,
    )
    return CapturedQuery(
        name=name,
        statement=session.scalars_statements[0],
        expectation=PlanExpectation(
            max_execution_ms=100.0,
            expected_index_names=(
                "cm_external_resource_name_en_trgm_idx",
                "cm_external_resource_name_ru_trgm_idx",
                "cm_external_resource_url_trgm_idx",
            ),
            forbidden_seq_scan_relations=("competency_matrix__external_resource_model",),
            allow_seq_scan_reason=None,
        ),
    )
