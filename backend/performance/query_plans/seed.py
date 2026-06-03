from datetime import UTC, datetime
from sys import stdout

from sqlalchemy import Integer, String, case, delete, func, insert, literal, select, text, union_all
from sqlalchemy import cast as sql_cast
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql.selectable import Subquery

from infra.postgresql.models import (
    CompetencyMatrixItemModel,
    ExternalResourceModel,
    NoteDailyAnalyticsModel,
    NoteModel,
    NoteReactionModel,
    NoteToTagSecondaryModel,
    TagModel,
)
from infra.postgresql.models.competency_matrix import ResourceToItemSecondaryModel
from performance.query_plans.models import DatasetProfile

SEED_NOW = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
PYTHON_ID = 1
POSTGRESQL_ID = 2
PYDANTIC_ID = 3
GENERAL_TAG_START_ID = 4
TARGET_NOTE_DIVISOR = 100


async def seed_profile(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    stdout.write(
        "Seeding query-plan dataset: "
        f"{profile.note_count} notes, {profile.tag_count} tags, "
        f"{profile.note_tag_link_count} note-tag links, {profile.resource_count} resources\n",
    )
    await connection.execute(text("SET LOCAL synchronous_commit = off"))
    await clear_seeded_tables(connection=connection)
    await insert_tags(connection=connection, profile=profile)
    await insert_notes(connection=connection, profile=profile)
    await insert_note_tag_links(connection=connection, profile=profile)
    await insert_resources(connection=connection, profile=profile)
    await insert_competency_matrix_items(connection=connection, profile=profile)


async def clear_seeded_tables(*, connection: AsyncConnection) -> None:
    for model in (
        ResourceToItemSecondaryModel,
        CompetencyMatrixItemModel,
        ExternalResourceModel,
        NoteReactionModel,
        NoteDailyAnalyticsModel,
        NoteToTagSecondaryModel,
        NoteModel,
        TagModel,
    ):
        await connection.execute(delete(model))


async def insert_tags(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    series = generate_series_subquery(end=profile.tag_count, name="tag_series")
    value = sql_cast(series.c.value, Integer)
    await connection.execute(
        insert(TagModel.__table__).from_select(
            ["id", "name_ru", "name_en", "slug", "deleted_at"],
            select(
                value,
                case(
                    (value == PYTHON_ID, literal("Питон")),
                    (value == POSTGRESQL_ID, literal("PostgreSQL")),
                    (value == PYDANTIC_ID, literal("Pydantic")),
                    else_=func.concat(literal("Тег "), value),
                ),
                case(
                    (value == PYTHON_ID, literal("Python")),
                    (value == POSTGRESQL_ID, literal("PostgreSQL")),
                    (value == PYDANTIC_ID, literal("Pydantic")),
                    else_=func.concat(literal("Tag "), value),
                ),
                case(
                    (value == PYTHON_ID, literal("python")),
                    (value == POSTGRESQL_ID, literal("postgresql")),
                    (value == PYDANTIC_ID, literal("pydantic")),
                    else_=func.concat(literal("tag-"), value),
                ),
                literal(None),
            ).select_from(series),
        ),
    )


async def insert_notes(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    series = generate_series_subquery(end=profile.note_count, name="note_series")
    value = sql_cast(series.c.value, Integer)
    target_note = func.mod(value, TARGET_NOTE_DIVISOR) == 0
    await connection.execute(
        insert(NoteModel.__table__).from_select(
            [
                "id",
                "title_ru",
                "title_en",
                "content_ru",
                "content_en",
                "slug",
                "folder_ru",
                "folder_en",
                "author_username",
                "published_at",
                "publish_status",
            ],
            select(
                deterministic_uuid_from_int(value=value),
                case(
                    (target_note, func.concat(literal("PostgreSQL полнотекстовый поиск "), value)),
                    else_=func.concat(literal("Заметка "), value),
                ),
                case(
                    (target_note, func.concat(literal("PostgreSQL full text search "), value)),
                    else_=func.concat(literal("Engineering note "), value),
                ),
                case(
                    (
                        target_note,
                        func.concat(
                            literal("Проверка полнотекстовый поиск PostgreSQL для заметки "),
                            value,
                        ),
                    ),
                    else_=func.concat(literal("Общий backend материал "), value),
                ),
                case(
                    (
                        target_note,
                        func.concat(
                            literal("Benchmark content for PostgreSQL full text search note "),
                            value,
                        ),
                    ),
                    else_=func.concat(literal("General backend content "), value),
                ),
                func.concat(literal("note-"), value),
                literal("База знаний"),
                literal("Knowledge base"),
                literal("benchmark"),
                literal(SEED_NOW),
                literal("PUBLISHED"),
            ).select_from(series),
        ),
    )


async def insert_note_tag_links(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    target_link_count = min(
        profile.note_count // TARGET_NOTE_DIVISOR,
        profile.note_tag_link_count // TARGET_NOTE_DIVISOR,
    )
    general_link_count = profile.note_tag_link_count - target_link_count

    target_series = generate_series_subquery(end=target_link_count, name="target_links")
    target_value = sql_cast(target_series.c.value, Integer)
    target_select = select(
        deterministic_uuid_from_int(value=target_value * TARGET_NOTE_DIVISOR),
        literal(POSTGRESQL_ID),
    ).select_from(target_series)

    general_series = generate_series_subquery(end=general_link_count, name="general_links")
    general_value = sql_cast(general_series.c.value, Integer)
    note_number = func.mod(general_value - 1, profile.note_count) + 1
    link_round = sql_cast((general_value - 1) / profile.note_count, Integer)
    tag_number = (
        func.mod(
            general_value + link_round * 9973,
            profile.tag_count - PYDANTIC_ID,
        )
        + GENERAL_TAG_START_ID
    )
    general_select = select(
        deterministic_uuid_from_int(value=note_number),
        tag_number,
    ).select_from(general_series)

    await connection.execute(
        insert(NoteToTagSecondaryModel.__table__).from_select(
            ["note_id", "tag_id"],
            union_all(target_select, general_select),
        ),
    )


async def insert_resources(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    series = generate_series_subquery(end=profile.resource_count, name="resource_series")
    value = sql_cast(series.c.value, Integer)
    await connection.execute(
        insert(ExternalResourceModel.__table__).from_select(
            ["id", "name_ru", "name_en", "url"],
            select(
                value,
                case(
                    (value == PYTHON_ID, literal("Документация Pydantic")),
                    (value == POSTGRESQL_ID, literal("Документация Python")),
                    else_=func.concat(literal("Ресурс "), value),
                ),
                case(
                    (value == PYTHON_ID, literal("Pydantic validation guide")),
                    (value == POSTGRESQL_ID, literal("Python documentation")),
                    else_=func.concat(literal("Resource "), value),
                ),
                case(
                    (value == PYTHON_ID, literal("https://docs.pydantic.dev/latest/")),
                    (value == POSTGRESQL_ID, literal("https://docs.python.org/3/")),
                    else_=func.concat(literal("https://example.com/resources/"), value),
                ),
            ).select_from(series),
        ),
    )


async def insert_competency_matrix_items(
    *,
    connection: AsyncConnection,
    profile: DatasetProfile,
) -> None:
    series = generate_series_subquery(end=profile.resource_count, name="matrix_item_series")
    value = sql_cast(series.c.value, Integer)
    await connection.execute(
        insert(CompetencyMatrixItemModel.__table__).from_select(
            [
                "id",
                "slug",
                "question_ru",
                "question_en",
                "answer_ru",
                "answer_en",
                "interview_expected_answer_ru",
                "interview_expected_answer_en",
                "sheet_key",
                "sheet_ru",
                "sheet_en",
                "section_ru",
                "section_en",
                "subsection_ru",
                "subsection_en",
                "grade",
                "published_at",
                "publish_status",
            ],
            select(
                value,
                func.concat(literal("matrix-question-"), value),
                func.concat(literal("Вопрос матрицы "), value),
                func.concat(literal("Matrix question "), value),
                func.concat(literal("Ответ матрицы "), value),
                func.concat(literal("Matrix answer "), value),
                func.concat(literal("Ожидаемый ответ "), value),
                func.concat(literal("Expected answer "), value),
                literal("python"),
                literal("Питон"),
                literal("Python"),
                literal("Основы"),
                literal("Basics"),
                literal("Функции"),
                literal("Functions"),
                literal("JUNIOR"),
                literal(SEED_NOW),
                literal("PUBLISHED"),
            ).select_from(series),
        ),
    )


def generate_series_subquery(*, end: int, name: str) -> Subquery:
    return select(func.generate_series(1, end).label("value")).subquery(name)


def deterministic_uuid_from_int(*, value: object) -> object:
    digest = func.md5(sql_cast(value, String))
    uuid_text = func.concat(
        func.substr(digest, 1, 8),
        literal("-"),
        func.substr(digest, 9, 4),
        literal("-"),
        func.substr(digest, 13, 4),
        literal("-"),
        func.substr(digest, 17, 4),
        literal("-"),
        func.substr(digest, 21, 12),
    )
    return sql_cast(uuid_text, postgresql.UUID(as_uuid=True))


async def vacuum_analyze_seeded_tables(*, connection: AsyncConnection) -> None:
    stdout.write("Running VACUUM ANALYZE for seeded query-plan tables\n")
    for table_name in (
        "notes__note_model",
        "notes__tag_model",
        "notes__note_to_tag_secondary_model",
        "competency_matrix__external_resource_model",
        "competency_matrix__competency_matrix_item_model",
    ):
        await connection.execute(text(f"VACUUM ANALYZE {table_name}"))
