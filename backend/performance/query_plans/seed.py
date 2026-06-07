from datetime import UTC, date, datetime, timedelta
from hashlib import md5
from sys import stdout
from uuid import UUID

from sqlalchemy import (
    Integer,
    String,
    case,
    delete,
    func,
    insert,
    literal,
    select,
    text,
    true,
    union_all,
)
from sqlalchemy import cast as sql_cast
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql.selectable import Subquery

from core.auth.enums import RoleEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from infra.postgresql.models import (
    CompetencyMatrixItemModel,
    ContactMeModel,
    ExternalResourceModel,
    NoteDailyAnalyticsModel,
    NoteModel,
    NoteReactionModel,
    NoteToTagSecondaryModel,
    QueuedQuestionModel,
    TagModel,
    UserModel,
)
from infra.postgresql.models.competency_matrix import ResourceToItemSecondaryModel
from performance.query_plans.models import DatasetProfile

SEED_NOW = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
SEED_USERNAME = "benchmark"
PYTHON_ID = 1
POSTGRESQL_ID = 2
PYDANTIC_ID = 3
GENERAL_TAG_START_ID = 4
TARGET_NOTE_DIVISOR = 100
USER_SEED_COUNT = 10_000
NOTE_REACTION_SEED_COUNT = 50_000
QUEUED_QUESTION_SEED_COUNT = 50_000


async def seed_profile(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    stdout.write(
        "Seeding query-plan dataset: "
        f"{profile.note_count} notes, {profile.tag_count} tags, "
        f"{profile.note_tag_link_count} note-tag links, {profile.resource_count} resources\n",
    )
    await connection.execute(text("SET LOCAL synchronous_commit = off"))
    await clear_seeded_tables(connection=connection)
    await insert_users(connection=connection)
    await insert_tags(connection=connection, profile=profile)
    await insert_notes(connection=connection, profile=profile)
    await insert_note_tag_links(connection=connection, profile=profile)
    await insert_note_analytics(connection=connection)
    await insert_note_reactions(connection=connection, profile=profile)
    await insert_resources(connection=connection, profile=profile)
    await insert_competency_matrix_items(connection=connection, profile=profile)
    await insert_competency_matrix_resource_links(connection=connection)
    await insert_queued_competency_matrix_questions(connection=connection)


async def clear_seeded_tables(*, connection: AsyncConnection) -> None:
    for model in (
        ResourceToItemSecondaryModel,
        QueuedQuestionModel,
        CompetencyMatrixItemModel,
        ExternalResourceModel,
        NoteReactionModel,
        NoteDailyAnalyticsModel,
        NoteToTagSecondaryModel,
        NoteModel,
        TagModel,
        ContactMeModel,
        UserModel,
    ):
        await connection.execute(delete(model))


async def insert_users(*, connection: AsyncConnection) -> None:
    series = generate_series_subquery(end=USER_SEED_COUNT, name="user_series")
    value = sql_cast(series.c.value, Integer)
    await connection.execute(
        insert(UserModel.__table__).from_select(
            ["username", "password_hash", "role"],
            select(
                case(
                    (value == 1, literal(SEED_USERNAME)),
                    else_=func.concat(literal("benchmark-user-"), value),
                ),
                func.concat(literal("query-plan-seed-password-hash-"), value),
                literal(RoleEnum.ADMIN.name),
            ).select_from(series),
        ),
    )


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
                case((value == GENERAL_TAG_START_ID, literal(SEED_NOW)), else_=literal(None)),
            ).select_from(series),
        ),
    )


async def insert_notes(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    series = generate_series_subquery(end=profile.note_count, name="note_series")
    value = sql_cast(series.c.value, Integer)
    target_note = func.mod(value, TARGET_NOTE_DIVISOR) == 0
    published_note = func.mod(value, 4) == 0
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
                case((published_note, literal(SEED_NOW)), else_=literal(None)),
                case((published_note, literal("PUBLISHED")), else_=literal("DRAFT")),
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


async def insert_note_analytics(*, connection: AsyncConnection) -> None:
    await connection.execute(
        insert(NoteDailyAnalyticsModel),
        [
            {
                "note_id": deterministic_python_uuid_from_int(value=note_number),
                "date": recorded_on,
                "source_category": source_category,
                "view_count": 100 + note_number,
                "engaged_view_count": 10 + note_number,
            }
            for note_number in (100, 200)
            for recorded_on in (date(2026, 1, 14), date(2026, 1, 15))
            for source_category in (
                NoteViewSourceCategory.DIRECT,
                NoteViewSourceCategory.SEARCH,
            )
        ],
    )


async def insert_note_reactions(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    reaction_count = min(profile.note_count, NOTE_REACTION_SEED_COUNT)
    series = generate_series_subquery(end=reaction_count, name="note_reaction_series")
    value = sql_cast(series.c.value, Integer)
    note_number = func.mod(value - 1, profile.note_count) + 1
    await connection.execute(
        insert(NoteReactionModel.__table__).from_select(
            [
                "note_id",
                "note_scoped_voter_hash",
                "reaction_kind",
                "created_at",
                "updated_at",
            ],
            select(
                deterministic_uuid_from_int(value=note_number),
                func.rpad(
                    func.concat(literal("query-plan-voter-"), value),
                    64,
                    literal("x"),
                ),
                case(
                    (func.mod(value, 2) == 0, literal(NoteReactionKind.HEART.name)),
                    else_=literal(NoteReactionKind.FIRE.name),
                ),
                literal(SEED_NOW),
                literal(SEED_NOW),
            ).select_from(series),
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
    sheet_bucket = func.mod(value, 20)
    python_sheet = sheet_bucket == 0
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
                case(
                    (python_sheet, literal("python")),
                    else_=func.concat(literal("sheet-"), sheet_bucket),
                ),
                case(
                    (python_sheet, literal("Питон")),
                    else_=func.concat(literal("Лист "), sheet_bucket),
                ),
                case(
                    (python_sheet, literal("Python")),
                    else_=func.concat(literal("Sheet "), sheet_bucket),
                ),
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


async def insert_competency_matrix_resource_links(*, connection: AsyncConnection) -> None:
    await connection.execute(
        insert(ResourceToItemSecondaryModel),
        [
            {
                "item_id": item_id,
                "resource_id": resource_id,
                "context_ru": "Контекст query-plan ресурса",
                "context_en": "Query-plan resource context",
            }
            for item_id in (100, 101)
            for resource_id in (PYTHON_ID, POSTGRESQL_ID)
        ],
    )


async def insert_queued_competency_matrix_questions(*, connection: AsyncConnection) -> None:
    await connection.execute(
        insert(QueuedQuestionModel.__table__),
        [
            {
                "id": value,
                "question": f"Queued matrix question {value}",
                "grade": "JUNIOR" if value % 5 == 0 else None,
                "sheet": "Python" if value % 7 == 0 else None,
                "section": "Basics" if value % 7 == 0 else None,
                "subsection": "Functions" if value % 7 == 0 else None,
                "suggested_by_username": SEED_USERNAME if value % 10 == 0 else None,
                "created_at": SEED_NOW + timedelta(seconds=value),
            }
            for value in range(1, QUEUED_QUESTION_SEED_COUNT + 1)
        ],
    )
    await connection.execute(
        select(
            func.setval(
                func.pg_get_serial_sequence(QueuedQuestionModel.__tablename__, "id"),
                QUEUED_QUESTION_SEED_COUNT,
                true(),
            ),
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


def deterministic_python_uuid_from_int(*, value: int) -> UUID:
    digest = md5(str(value).encode(), usedforsecurity=False).hexdigest()
    return UUID(
        f"{digest[0:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}",
    )


async def vacuum_analyze_seeded_tables(*, connection: AsyncConnection) -> None:
    stdout.write("Running VACUUM ANALYZE for seeded query-plan tables\n")
    for table_name in (
        "notes__note_model",
        "notes__tag_model",
        "notes__note_to_tag_secondary_model",
        "notes__note_daily_analytics_model",
        "notes__note_reaction_model",
        "competency_matrix__external_resource_model",
        "competency_matrix__competency_matrix_item_model",
        "competency_matrix__resource_to_item_secondary_model",
        "competency_matrix__queued_question_model",
        "auth__user_model",
    ):
        await connection.execute(text(f"VACUUM ANALYZE {table_name}"))
