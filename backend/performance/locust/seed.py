import asyncio
from datetime import UTC, date, datetime, timedelta
from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.articles.enums import ArticleReactionKind, ArticleViewSourceCategory
from core.auth.enums import RoleEnum
from core.competency_matrix.enums import InterviewFrequencyEnum
from core.enums import PublishStatusEnum
from infra.config.loggers import logger
from infra.postgresql.meta import sessionmaker
from infra.postgresql.models import (
    ArticleDailyAnalyticsModel,
    ArticleModel,
    ArticleReactionModel,
    ArticleToTagSecondaryModel,
    CompetencyMatrixItemModel,
    CompetencyMatrixSectionModel,
    CompetencyMatrixSheetModel,
    CompetencyMatrixSubsectionModel,
    ExternalResourceModel,
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
SEED_ARTICLE_COUNT = 48
SEED_MATRIX_ITEMS_PER_SHEET = 12
SEED_BASE_ID = 880000
SEED_START = datetime(2026, 3, 1, 10, tzinfo=UTC)
ARTICLE_SOURCE_CATEGORIES = (
    ArticleViewSourceCategory.DIRECT,
    ArticleViewSourceCategory.SEARCH,
    ArticleViewSourceCategory.INTERNAL,
)
REACTION_KINDS = (
    ArticleReactionKind.HEART,
    ArticleReactionKind.FIRE,
    ArticleReactionKind.THINKING,
    ArticleReactionKind.NEUTRAL,
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
    await insert_seed_articles(session=session)
    await insert_seed_article_tags(session=session)
    await insert_seed_article_analytics(session=session)
    await insert_seed_article_reactions(session=session)
    await insert_seed_matrix_resources(session=session)
    await insert_seed_matrix_structure(session=session)
    await insert_seed_matrix_items(session=session)
    await insert_seed_matrix_resource_links(session=session)


async def clear_seeded_data(*, session: AsyncSession) -> None:
    seeded_article_ids = [article_id(article_index) for article_index in article_range()]
    await session.execute(
        delete(ArticleReactionModel).where(
            ArticleReactionModel.article_id.in_(seeded_article_ids),
        ),
    )
    await session.execute(
        delete(ArticleDailyAnalyticsModel).where(
            ArticleDailyAnalyticsModel.article_id.in_(seeded_article_ids),
        ),
    )
    await session.execute(
        delete(ArticleToTagSecondaryModel).where(
            ArticleToTagSecondaryModel.article_id.in_(seeded_article_ids),
        ),
    )
    await session.execute(delete(ArticleModel).where(ArticleModel.slug.like("perf-seed-article-%")))
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
        delete(CompetencyMatrixSubsectionModel).where(
            CompetencyMatrixSubsectionModel.id.in_(
                [matrix_subsection_id(sheet_index) for sheet_index in matrix_sheet_indexes()],
            ),
        ),
    )
    await session.execute(
        delete(CompetencyMatrixSectionModel).where(
            CompetencyMatrixSectionModel.id.in_(
                [matrix_section_id(sheet_index) for sheet_index in matrix_sheet_indexes()],
            ),
        ),
    )
    await session.execute(
        delete(CompetencyMatrixSheetModel).where(
            CompetencyMatrixSheetModel.id.in_(
                [matrix_sheet_id(sheet_index) for sheet_index in matrix_sheet_indexes()],
            ),
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


async def insert_seed_articles(*, session: AsyncSession) -> None:
    await session.execute(
        insert(ArticleModel),
        [article_row(article_index=article_index) for article_index in article_range()],
    )


async def insert_seed_article_tags(*, session: AsyncSession) -> None:
    rows = [
        {"article_id": article_id(article_index), "tag_id": tag_id(tag_index)}
        for article_index in article_range()
        for tag_index in article_tag_indexes(article_index=article_index)
    ]
    await session.execute(insert(ArticleToTagSecondaryModel), rows)


async def insert_seed_article_analytics(*, session: AsyncSession) -> None:
    rows = [
        {
            "article_id": article_id(article_index),
            "date": date(2026, 6, 5) - timedelta(days=day_offset),
            "source_category": source_category,
            "view_count": 10 + article_index * 3 + day_offset,
            "engaged_view_count": 2 + article_index + day_offset,
        }
        for article_index in article_range()
        if article_is_published(article_index=article_index)
        for day_offset in range(3)
        for source_category in ARTICLE_SOURCE_CATEGORIES
    ]
    await session.execute(insert(ArticleDailyAnalyticsModel), rows)


async def insert_seed_article_reactions(*, session: AsyncSession) -> None:
    rows = [
        {
            "article_id": article_id(article_index),
            "article_scoped_voter_hash": f"{article_index:02d}{voter_index:02d}".ljust(64, "a"),
            "reaction_kind": REACTION_KINDS[(article_index + voter_index) % len(REACTION_KINDS)],
            "created_at": SEED_START + timedelta(hours=article_index + voter_index),
            "updated_at": SEED_START + timedelta(hours=article_index + voter_index, minutes=15),
        }
        for article_index in article_range()
        if article_is_published(article_index=article_index)
        for voter_index in range(1, 4)
    ]
    await session.execute(insert(ArticleReactionModel), rows)


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


async def insert_seed_matrix_structure(*, session: AsyncSession) -> None:
    await session.execute(
        insert(CompetencyMatrixSheetModel),
        [
            {
                "id": matrix_sheet_id(sheet_index),
                "key": sheet_key,
                "name_ru": sheet_ru,
                "name_en": sheet_en,
            }
            for sheet_index, (sheet_key, sheet_ru, sheet_en, _section_ru, _section_en) in enumerate(
                MATRIX_SHEETS,
            )
        ],
    )
    await session.execute(
        insert(CompetencyMatrixSectionModel),
        [
            {
                "id": matrix_section_id(sheet_index),
                "sheet_id": matrix_sheet_id(sheet_index),
                "name_ru": section_ru,
                "name_en": section_en,
            }
            for sheet_index, (
                _sheet_key,
                _sheet_ru,
                _sheet_en,
                section_ru,
                section_en,
            ) in enumerate(
                MATRIX_SHEETS,
            )
        ],
    )
    await session.execute(
        insert(CompetencyMatrixSubsectionModel),
        [
            {
                "id": matrix_subsection_id(sheet_index),
                "section_id": matrix_section_id(sheet_index),
                "name_ru": "Baseline",
                "name_en": "Baseline",
            }
            for sheet_index in matrix_sheet_indexes()
        ],
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


def article_row(*, article_index: int) -> dict[str, object]:
    publish_status = (
        PublishStatusEnum.PUBLISHED
        if article_is_published(article_index=article_index)
        else PublishStatusEnum.DRAFT
    )
    published_at = (
        SEED_START + timedelta(hours=article_index)
        if article_is_published(article_index=article_index)
        else None
    )
    matrix_slug = matrix_slug_for_index(item_index=((article_index - 1) % matrix_item_count()) + 1)
    return {
        "id": article_id(article_index),
        "title_ru": f"Performance seed статья {article_index}",
        "title_en": f"Performance seed article {article_index}",
        "content_ru": (
            f"# Performance seed статья {article_index}\n\n"
            "Эта статья нагружает публичный detail, список и дерево статей. "
            f"Связанный вопрос: [[matrix:{matrix_slug}|вопрос матрицы]]."
        ),
        "content_en": (
            f"# Performance seed article {article_index}\n\n"
            "This article exercises public article detail, list, and tree endpoints. "
            f"Related question: [[matrix:{matrix_slug}|matrix question]]."
        ),
        "slug": article_slug(article_index=article_index),
        "folder_ru": "Производительность",
        "folder_en": "Performance",
        "author_username": SEED_AUTHOR_USERNAME,
        "seo_title_ru": f"Performance seed статья {article_index}",
        "seo_title_en": f"Performance seed article {article_index}",
        "seo_description_ru": f"Seeded описание статьи {article_index} для Locust baseline.",
        "seo_description_en": (
            f"Seeded article {article_index} description for the Locust baseline."
        ),
        "cover_image_url": None,
        "cover_image_alt_ru": None,
        "cover_image_alt_en": None,
        "published_at": published_at,
        "publish_status": publish_status,
        "created_at": SEED_START - timedelta(days=1),
        "updated_at": SEED_START + timedelta(hours=article_index, minutes=30),
    }


def matrix_item_row(*, item_index: int) -> dict[str, object]:
    sheet_index = (item_index - 1) // SEED_MATRIX_ITEMS_PER_SHEET
    _sheet_key, sheet_ru, sheet_en, _section_ru, _section_en = MATRIX_SHEETS[sheet_index]
    question_number = ((item_index - 1) % SEED_MATRIX_ITEMS_PER_SHEET) + 1
    return {
        "id": matrix_item_id(item_index),
        "slug": matrix_slug_for_index(item_index=item_index),
        "question_ru": f"{sheet_ru}: как проверить performance сценарий {question_number}?",
        "question_en": f"{sheet_en}: how do you verify performance scenario {question_number}?",
        "answer_ru": (
            "Нужно назвать реальные данные, warm/cold cache, p95, average и критерий отката. "
            f"Связанная статья: [[articles:{article_slug(article_index=question_number)}]]."
        ),
        "answer_en": (
            "Name realistic data, warm/cold cache, p95, average, and rollback criteria. "
            f"Related article: [[articles:{article_slug(article_index=question_number)}]]."
        ),
        "interview_expected_answer_ru": "Ожидается конкретный план проверки и сравнения baseline.",
        "interview_expected_answer_en": (
            "Expected answer gives a concrete baseline comparison plan."
        ),
        "subsection_id": matrix_subsection_id(sheet_index),
        "grade": grade_for_index(item_index=item_index),
        "interview_frequency": interview_frequency_for_index(item_index=item_index),
        "published_at": SEED_START + timedelta(hours=item_index),
        "publish_status": PublishStatusEnum.PUBLISHED,
    }


def grade_for_index(*, item_index: int) -> str:
    grades = ("JUNIOR", "JUNIOR_PLUS", "MIDDLE", "MIDDLE_PLUS", "SENIOR")
    return grades[(item_index - 1) % len(grades)]


def interview_frequency_for_index(*, item_index: int) -> str | None:
    frequencies = (
        InterviewFrequencyEnum.CONSTANTLY.name,
        InterviewFrequencyEnum.OFTEN.name,
        InterviewFrequencyEnum.RARELY.name,
        InterviewFrequencyEnum.NEVER_SEEN.name,
        None,
    )
    return frequencies[(item_index - 1) % len(frequencies)]


def article_tag_indexes(*, article_index: int) -> tuple[int, int]:
    primary_index = 1
    secondary_index = ((article_index - 1) % len(TAG_SPECS)) + 1
    if secondary_index == primary_index:
        secondary_index = 2
    return primary_index, secondary_index


def linked_resource_indexes(*, item_index: int) -> tuple[int, int]:
    return ((item_index - 1) % resource_count()) + 1, (item_index % resource_count()) + 1


def article_id(article_index: int) -> UUID:
    return UUID(f"20000000-0000-4000-8000-{article_index:012d}")


def article_slug(*, article_index: int) -> str:
    return f"perf-seed-article-{article_index:03d}"


def matrix_slug_for_index(*, item_index: int) -> str:
    sheet_index = (item_index - 1) // SEED_MATRIX_ITEMS_PER_SHEET
    sheet_key = MATRIX_SHEETS[sheet_index][0]
    return f"perf-seed-matrix-{item_index:03d}-{sheet_key}"


def article_is_published(*, article_index: int) -> bool:
    return article_index % 10 != 0


def article_range() -> range:
    return range(1, SEED_ARTICLE_COUNT + 1)


def matrix_item_range() -> range:
    return range(1, matrix_item_count() + 1)


def matrix_sheet_indexes() -> range:
    return range(len(MATRIX_SHEETS))


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


def matrix_sheet_id(sheet_index: int) -> int:
    return SEED_BASE_ID + 300 + sheet_index


def matrix_section_id(sheet_index: int) -> int:
    return SEED_BASE_ID + 400 + sheet_index


def matrix_subsection_id(sheet_index: int) -> int:
    return SEED_BASE_ID + 500 + sheet_index


def main() -> None:
    asyncio.run(run_seed_from_settings(config=settings.seed))


if __name__ == "__main__":
    main()
