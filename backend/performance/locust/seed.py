import asyncio
from datetime import UTC, date, datetime, timedelta
from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.enums import RoleEnum
from core.enums import PublishStatusEnum
from core.notes.enums import NoteReactionKind, NoteViewSourceCategory
from infra.config.loggers import logger
from infra.postgresql.meta import sessionmaker
from infra.postgresql.models import (
    CompetencyMatrixItemModel,
    ExternalResourceModel,
    NoteDailyAnalyticsModel,
    NoteModel,
    NoteReactionModel,
    NoteToTagSecondaryModel,
    TagModel,
    UserModel,
)
from infra.postgresql.models.competency_matrix import ResourceToItemSecondaryModel
from performance.locust.settings import (
    LocustSeedConfig,
    settings,
)

LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "::1"})  # noqa: S104
SEED_AUTHOR_USERNAME = "performance-seed-admin"
SEED_PASSWORD_HASH = "performance-seed-password-hash"  # noqa: S105
SEED_NOTE_COUNT = 48
SEED_MATRIX_ITEMS_PER_SHEET = 12
SEED_BASE_ID = 880000
SEED_START = datetime(2026, 3, 1, 10, tzinfo=UTC)
NOTE_SOURCE_CATEGORIES = (
    NoteViewSourceCategory.DIRECT,
    NoteViewSourceCategory.SEARCH,
    NoteViewSourceCategory.INTERNAL,
)
REACTION_KINDS = (
    NoteReactionKind.HEART,
    NoteReactionKind.FIRE,
    NoteReactionKind.THINKING,
    NoteReactionKind.NEUTRAL,
)
MATRIX_SHEETS = (
    ("python", "Питон", "Python", "Язык", "Language"),
    ("backend", "Бэкенд", "Backend", "API", "API"),
    ("databases", "Базы данных", "Databases", "PostgreSQL", "PostgreSQL"),
    ("frontend", "Фронтенд", "Frontend", "SSR", "SSR"),
    ("quality", "Качество", "Quality", "Performance", "Performance"),
)
TAG_SPECS = (
    ("performance", "Производительность", "Performance"),
    ("python", "Python", "Python"),
    ("backend", "Бэкенд", "Backend"),
    ("postgres", "PostgreSQL", "PostgreSQL"),
    ("frontend", "Фронтенд", "Frontend"),
    ("quality", "Качество", "Quality"),
)


def validate_seed_config(config: LocustSeedConfig) -> bool:
    if not config.seed.seed_data:
        return False
    if host_from_url(config.seed.host) not in LOCAL_HOSTS:
        msg = "PERFORMANCE_SEED_DATA requires a local target"
        raise ValueError(msg)
    if config.database.host not in LOCAL_HOSTS:
        msg = "PERFORMANCE_SEED_DATA requires a local database host"
        raise ValueError(msg)
    if "test" not in config.database.name:
        msg = "PERFORMANCE_SEED_DATA requires a test database"
        raise ValueError(msg)
    return True


def host_from_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.hostname is not None:
        return parsed.hostname
    return value.split(":", maxsplit=1)[0]


async def run_seed_from_settings(config: LocustSeedConfig) -> None:
    if not validate_seed_config(config):
        logger.info("Performance seed skipped")
        return
    async with sessionmaker() as session:
        await seed_performance_data(session=session)
        await session.commit()
    logger.info("Performance seed completed")


async def seed_performance_data(*, session: AsyncSession) -> None:
    await clear_seeded_data(session=session)
    await insert_seed_user(session=session)
    await insert_seed_tags(session=session)
    await insert_seed_notes(session=session)
    await insert_seed_note_tags(session=session)
    await insert_seed_note_analytics(session=session)
    await insert_seed_note_reactions(session=session)
    await insert_seed_matrix_resources(session=session)
    await insert_seed_matrix_items(session=session)
    await insert_seed_matrix_resource_links(session=session)


async def clear_seeded_data(*, session: AsyncSession) -> None:
    seeded_note_ids = [note_id(note_index) for note_index in note_range()]
    await session.execute(
        delete(NoteReactionModel).where(
            NoteReactionModel.note_id.in_(seeded_note_ids),
        ),
    )
    await session.execute(
        delete(NoteDailyAnalyticsModel).where(
            NoteDailyAnalyticsModel.note_id.in_(seeded_note_ids),
        ),
    )
    await session.execute(
        delete(NoteToTagSecondaryModel).where(
            NoteToTagSecondaryModel.note_id.in_(seeded_note_ids),
        ),
    )
    await session.execute(delete(NoteModel).where(NoteModel.slug.like("perf-seed-note-%")))
    await session.execute(delete(TagModel).where(TagModel.slug.like("perf-seed-%")))
    await session.execute(
        delete(ResourceToItemSecondaryModel).where(
            ResourceToItemSecondaryModel.item_id.in_(
                [matrix_item_id(item_index) for item_index in matrix_item_range()],
            ),
        ),
    )
    await session.execute(
        delete(CompetencyMatrixItemModel).where(
            CompetencyMatrixItemModel.slug.like("perf-seed-matrix-%"),
        ),
    )
    await session.execute(
        delete(ExternalResourceModel).where(
            ExternalResourceModel.url.like("https://performance.example.test/%"),
        ),
    )
    await session.execute(delete(UserModel).where(UserModel.username == SEED_AUTHOR_USERNAME))


async def insert_seed_user(*, session: AsyncSession) -> None:
    await session.execute(
        insert(UserModel).values(
            username=SEED_AUTHOR_USERNAME,
            password_hash=SEED_PASSWORD_HASH,
            role=RoleEnum.ADMIN,
        ),
    )


async def insert_seed_tags(*, session: AsyncSession) -> None:
    await session.execute(
        insert(TagModel),
        [
            {
                "id": tag_id(tag_index),
                "name_ru": name_ru,
                "name_en": name_en,
                "slug": f"perf-seed-{slug}",
                "deleted_at": None,
            }
            for tag_index, (slug, name_ru, name_en) in enumerate(TAG_SPECS, start=1)
        ],
    )


async def insert_seed_notes(*, session: AsyncSession) -> None:
    await session.execute(
        insert(NoteModel),
        [note_row(note_index=note_index) for note_index in note_range()],
    )


async def insert_seed_note_tags(*, session: AsyncSession) -> None:
    rows = [
        {"note_id": note_id(note_index), "tag_id": tag_id(tag_index)}
        for note_index in note_range()
        for tag_index in note_tag_indexes(note_index=note_index)
    ]
    await session.execute(insert(NoteToTagSecondaryModel), rows)


async def insert_seed_note_analytics(*, session: AsyncSession) -> None:
    rows = [
        {
            "note_id": note_id(note_index),
            "date": date(2026, 6, 5) - timedelta(days=day_offset),
            "source_category": source_category,
            "view_count": 10 + note_index * 3 + day_offset,
            "engaged_view_count": 2 + note_index + day_offset,
        }
        for note_index in note_range()
        if note_is_published(note_index=note_index)
        for day_offset in range(3)
        for source_category in NOTE_SOURCE_CATEGORIES
    ]
    await session.execute(insert(NoteDailyAnalyticsModel), rows)


async def insert_seed_note_reactions(*, session: AsyncSession) -> None:
    rows = [
        {
            "note_id": note_id(note_index),
            "note_scoped_voter_hash": f"{note_index:02d}{voter_index:02d}".ljust(64, "a"),
            "reaction_kind": REACTION_KINDS[(note_index + voter_index) % len(REACTION_KINDS)],
            "created_at": SEED_START + timedelta(hours=note_index + voter_index),
            "updated_at": SEED_START + timedelta(hours=note_index + voter_index, minutes=15),
        }
        for note_index in note_range()
        if note_is_published(note_index=note_index)
        for voter_index in range(1, 4)
    ]
    await session.execute(insert(NoteReactionModel), rows)


async def insert_seed_matrix_resources(*, session: AsyncSession) -> None:
    await session.execute(
        insert(ExternalResourceModel),
        [
            {
                "id": matrix_resource_id(resource_index),
                "name_ru": f"Performance Python ресурс {resource_index}",
                "name_en": f"Performance Python resource {resource_index}",
                "url": f"https://performance.example.test/resources/{resource_index}",
            }
            for resource_index in resource_range()
        ],
    )


async def insert_seed_matrix_items(*, session: AsyncSession) -> None:
    await session.execute(
        insert(CompetencyMatrixItemModel),
        [matrix_item_row(item_index=item_index) for item_index in matrix_item_range()],
    )


async def insert_seed_matrix_resource_links(*, session: AsyncSession) -> None:
    rows = [
        {
            "item_id": matrix_item_id(item_index),
            "resource_id": matrix_resource_id(resource_index),
            "context_ru": f"Контекст ресурса {resource_index} для вопроса {item_index}",
            "context_en": f"Resource {resource_index} context for question {item_index}",
        }
        for item_index in matrix_item_range()
        for resource_index in linked_resource_indexes(item_index=item_index)
    ]
    await session.execute(insert(ResourceToItemSecondaryModel), rows)


def note_row(*, note_index: int) -> dict[str, object]:
    publish_status = (
        PublishStatusEnum.PUBLISHED
        if note_is_published(note_index=note_index)
        else PublishStatusEnum.DRAFT
    )
    published_at = (
        SEED_START + timedelta(hours=note_index)
        if note_is_published(note_index=note_index)
        else None
    )
    matrix_slug = matrix_slug_for_index(item_index=((note_index - 1) % matrix_item_count()) + 1)
    return {
        "id": note_id(note_index),
        "title_ru": f"Performance seed заметка {note_index}",
        "title_en": f"Performance seed note {note_index}",
        "content_ru": (
            f"# Performance seed заметка {note_index}\n\n"
            "Эта заметка нагружает публичный detail, список и дерево заметок. "
            f"Связанный вопрос: [[matrix:{matrix_slug}|вопрос матрицы]]."
        ),
        "content_en": (
            f"# Performance seed note {note_index}\n\n"
            "This note exercises public note detail, list, and tree endpoints. "
            f"Related question: [[matrix:{matrix_slug}|matrix question]]."
        ),
        "slug": note_slug(note_index=note_index),
        "folder_ru": "Производительность",
        "folder_en": "Performance",
        "author_username": SEED_AUTHOR_USERNAME,
        "seo_title_ru": f"Performance seed заметка {note_index}",
        "seo_title_en": f"Performance seed note {note_index}",
        "seo_description_ru": f"Seeded описание заметки {note_index} для Locust baseline.",
        "seo_description_en": f"Seeded note {note_index} description for the Locust baseline.",
        "cover_image_url": None,
        "cover_image_alt_ru": None,
        "cover_image_alt_en": None,
        "published_at": published_at,
        "publish_status": publish_status,
        "created_at": SEED_START - timedelta(days=1),
        "updated_at": SEED_START + timedelta(hours=note_index, minutes=30),
    }


def matrix_item_row(*, item_index: int) -> dict[str, object]:
    sheet_index = (item_index - 1) // SEED_MATRIX_ITEMS_PER_SHEET
    sheet_key, sheet_ru, sheet_en, section_ru, section_en = MATRIX_SHEETS[sheet_index]
    question_number = ((item_index - 1) % SEED_MATRIX_ITEMS_PER_SHEET) + 1
    return {
        "id": matrix_item_id(item_index),
        "slug": matrix_slug_for_index(item_index=item_index),
        "question_ru": f"{sheet_ru}: как проверить performance сценарий {question_number}?",
        "question_en": f"{sheet_en}: how do you verify performance scenario {question_number}?",
        "answer_ru": (
            "Нужно назвать реальные данные, warm/cold cache, p95, average и критерий отката. "
            f"Связанная заметка: [[notes:{note_slug(note_index=question_number)}]]."
        ),
        "answer_en": (
            "Name realistic data, warm/cold cache, p95, average, and rollback criteria. "
            f"Related note: [[notes:{note_slug(note_index=question_number)}]]."
        ),
        "interview_expected_answer_ru": "Ожидается конкретный план проверки и сравнения baseline.",
        "interview_expected_answer_en": (
            "Expected answer gives a concrete baseline comparison plan."
        ),
        "sheet_key": sheet_key,
        "sheet_ru": sheet_ru,
        "sheet_en": sheet_en,
        "section_ru": section_ru,
        "section_en": section_en,
        "subsection_ru": "Baseline",
        "subsection_en": "Baseline",
        "grade": grade_for_index(item_index=item_index),
        "published_at": SEED_START + timedelta(hours=item_index),
        "publish_status": PublishStatusEnum.PUBLISHED,
    }


def grade_for_index(*, item_index: int) -> str:
    grades = ("JUNIOR", "JUNIOR_PLUS", "MIDDLE", "MIDDLE_PLUS", "SENIOR")
    return grades[(item_index - 1) % len(grades)]


def note_tag_indexes(*, note_index: int) -> tuple[int, int]:
    primary_index = 1
    secondary_index = ((note_index - 1) % len(TAG_SPECS)) + 1
    if secondary_index == primary_index:
        secondary_index = 2
    return primary_index, secondary_index


def linked_resource_indexes(*, item_index: int) -> tuple[int, int]:
    return ((item_index - 1) % resource_count()) + 1, (item_index % resource_count()) + 1


def note_id(note_index: int) -> UUID:
    return UUID(f"20000000-0000-4000-8000-{note_index:012d}")


def note_slug(*, note_index: int) -> str:
    return f"perf-seed-note-{note_index:03d}"


def matrix_slug_for_index(*, item_index: int) -> str:
    sheet_index = (item_index - 1) // SEED_MATRIX_ITEMS_PER_SHEET
    sheet_key = MATRIX_SHEETS[sheet_index][0]
    return f"perf-seed-matrix-{item_index:03d}-{sheet_key}"


def note_is_published(*, note_index: int) -> bool:
    return note_index % 10 != 0


def note_range() -> range:
    return range(1, SEED_NOTE_COUNT + 1)


def matrix_item_range() -> range:
    return range(1, matrix_item_count() + 1)


def resource_range() -> range:
    return range(1, resource_count() + 1)


def matrix_item_count() -> int:
    return len(MATRIX_SHEETS) * SEED_MATRIX_ITEMS_PER_SHEET


def resource_count() -> int:
    return len(MATRIX_SHEETS) * 2


def tag_id(tag_index: int) -> int:
    return SEED_BASE_ID + tag_index


def matrix_resource_id(resource_index: int) -> int:
    return SEED_BASE_ID + 100 + resource_index


def matrix_item_id(item_index: int) -> int:
    return SEED_BASE_ID + 200 + item_index


def main() -> None:
    asyncio.run(run_seed_from_settings(config=settings.seed))


if __name__ == "__main__":
    main()
