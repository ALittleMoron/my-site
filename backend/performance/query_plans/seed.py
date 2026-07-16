from datetime import UTC, date, datetime, timedelta
from hashlib import md5
from sys import stdout

from sqlalchemy import (
    Integer,
    String,
    case,
    func,
    insert,
    literal,
    select,
    text,
    union_all,
)
from sqlalchemy import and_ as sa_and
from sqlalchemy import cast as sql_cast
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql.selectable import Subquery

from core.agent_access.enums import (
    AgentActionEnum,
    AgentAuditResultEnum,
    AgentClientStatusEnum,
    AgentScopeEnum,
)
from core.articles.enums import ArticleReactionKind, ArticleViewSourceCategory
from core.auth.enums import AuthSessionAuthMethodEnum, AuthSessionDeviceTypeEnum, RoleEnum
from core.competency_matrix.schemas import CompetencyMatrixQuestionFingerprint
from core.i18n.enums import LanguageEnum
from infra.postgresql.models import (
    AgentAuditEventModel,
    AgentCertificateModel,
    AgentCertificateRotationModel,
    AgentClientModel,
    ArticleDailyAnalyticsModel,
    ArticleFolderModel,
    ArticleModel,
    ArticleReactionModel,
    ArticleToTagSecondaryModel,
    AuthSessionModel,
    CompetencyMatrixItemModel,
    CompetencyMatrixSectionModel,
    CompetencyMatrixSheetModel,
    CompetencyMatrixSubsectionModel,
    ContactMeModel,
    ExternalResourceModel,
    MatrixQuestionClaimModel,
    MatrixQuestionDraftCompletionModel,
    QueuedQuestionModel,
    ResumeModel,
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
ARTICLE_FOLDER_ID = "30000000000040008000000000000001"
TARGET_ARTICLE_DIVISOR = 100
MATRIX_GRADE_BUCKET_MIDDLE = 2
MATRIX_GRADE_BUCKET_MIDDLE_PLUS = 3
MATRIX_FREQUENCY_BUCKET_RARELY = 2
MATRIX_FREQUENCY_BUCKET_NEVER_SEEN = 3
USER_SEED_COUNT = 10_000
AUTH_SESSION_SEED_COUNT = 1_000
INACTIVE_MODERATOR_SEED_INDEX = 2
OWNER_SEED_INDEX = 3
MANAGED_ACCOUNT_ROLE_BUCKET_DIVISOR = 100
MANAGED_ACCOUNT_MODERATOR_BUCKET_REMAINDER = 50
ARTICLE_REACTION_SEED_COUNT = 50_000
QUEUED_QUESTION_SEED_COUNT = 50_000
RESUME_SEED_COUNT = 50_000
QUERY_PLAN_SEEDED_MODELS = (
    AgentAuditEventModel,
    MatrixQuestionDraftCompletionModel,
    AgentCertificateRotationModel,
    MatrixQuestionClaimModel,
    AgentCertificateModel,
    AgentClientModel,
    ResourceToItemSecondaryModel,
    QueuedQuestionModel,
    CompetencyMatrixItemModel,
    CompetencyMatrixSubsectionModel,
    CompetencyMatrixSectionModel,
    CompetencyMatrixSheetModel,
    ExternalResourceModel,
    ArticleReactionModel,
    ArticleDailyAnalyticsModel,
    ArticleToTagSecondaryModel,
    ArticleModel,
    ArticleFolderModel,
    TagModel,
    ResumeModel,
    ContactMeModel,
    AuthSessionModel,
    UserModel,
)
QUERY_PLAN_RESET_SQL = (
    "TRUNCATE TABLE "
    + ", ".join(model.__table__.name for model in QUERY_PLAN_SEEDED_MODELS)
    + " RESTART IDENTITY CASCADE"
)
RESUME_SEED_CONTENT: dict[str, object] = {
    "profile": {
        "full_name": "Query Plan Candidate",
        "role": "Engineer",
        "location": "",
        "email": "",
        "phone": "",
        "website_url": "",
        "linkedin_url": "",
        "github_url": "",
        "telegram": "",
    },
    "summary": {
        "text": "Resume for query-plan smoke.",
    },
    "skills": [],
    "experience": [],
    "education": [],
    "languages": [],
    "certifications": [],
    "additional_sections": [],
}


async def seed_profile(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    stdout.write(
        "Seeding query-plan dataset: "
        f"{profile.article_count} articles, {profile.tag_count} tags, "
        f"{profile.article_tag_link_count} article-tag links, {profile.resource_count} resources, "
        f"{RESUME_SEED_COUNT} resumes\n",
    )
    await connection.execute(text("SET LOCAL synchronous_commit = off"))
    await clear_seeded_tables(connection=connection)
    await insert_users(connection=connection)
    await insert_auth_sessions(connection=connection)
    await insert_tags(connection=connection, profile=profile)
    await insert_article_folders(connection=connection)
    await insert_articles(connection=connection, profile=profile)
    await insert_article_tag_links(connection=connection, profile=profile)
    await insert_article_analytics(connection=connection)
    await insert_article_reactions(connection=connection, profile=profile)
    await insert_resumes(connection=connection)
    await insert_resources(connection=connection, profile=profile)
    await insert_competency_matrix_structure(connection=connection)
    await insert_competency_matrix_items(connection=connection, profile=profile)
    await insert_competency_matrix_resource_links(connection=connection)
    await insert_queued_competency_matrix_questions(connection=connection)
    await insert_agent_access_records(connection=connection)


async def clear_seeded_tables(*, connection: AsyncConnection) -> None:
    await connection.execute(text(QUERY_PLAN_RESET_SQL))


async def insert_users(*, connection: AsyncConnection) -> None:
    series = generate_series_subquery(end=USER_SEED_COUNT, name="user_series")
    value = sql_cast(series.c.value, Integer)
    await connection.execute(
        insert(UserModel.__table__).from_select(
            ["username", "password_hash", "role", "is_active"],
            select(
                case(
                    (value == 1, literal(SEED_USERNAME)),
                    else_=func.concat(literal("benchmark-user-"), value),
                ),
                func.concat(literal("query-plan-seed-password-hash-"), value),
                sql_cast(
                    case(
                        (value == 1, literal(RoleEnum.ADMIN.name)),
                        (value == INACTIVE_MODERATOR_SEED_INDEX, literal(RoleEnum.MODERATOR.name)),
                        (value == OWNER_SEED_INDEX, literal(RoleEnum.OWNER.name)),
                        (
                            value % MANAGED_ACCOUNT_ROLE_BUCKET_DIVISOR == 0,
                            literal(RoleEnum.ADMIN.name),
                        ),
                        (
                            value % MANAGED_ACCOUNT_ROLE_BUCKET_DIVISOR
                            == MANAGED_ACCOUNT_MODERATOR_BUCKET_REMAINDER,
                            literal(RoleEnum.MODERATOR.name),
                        ),
                        else_=literal(RoleEnum.USER.name),
                    ),
                    UserModel.__table__.c.role.type,
                ),
                case(
                    (value == INACTIVE_MODERATOR_SEED_INDEX, literal(value=False)),
                    else_=literal(value=True),
                ),
            ).select_from(series),
        ),
    )


async def insert_auth_sessions(*, connection: AsyncConnection) -> None:
    series = generate_series_subquery(end=AUTH_SESSION_SEED_COUNT, name="auth_session_series")
    value = sql_cast(series.c.value, Integer)
    await connection.execute(
        insert(AuthSessionModel.__table__).from_select(
            [
                "id",
                "username",
                "secret_hash",
                "expires_at",
                "absolute_expires_at",
                "is_revoked",
                "last_used_at",
                "auth_method",
                "user_agent_display",
                "user_agent_browser",
                "user_agent_os",
                "user_agent_device",
            ],
            select(
                hex_id_expr(value=value),
                case(
                    (value == 1, literal(SEED_USERNAME)),
                    else_=func.concat(literal("benchmark-user-"), value),
                ),
                func.concat(
                    deterministic_hex_from_int(value=func.concat(literal("session-a-"), value)),
                    deterministic_hex_from_int(value=func.concat(literal("session-b-"), value)),
                ),
                case(
                    (value % 10 == 0, literal(SEED_NOW - timedelta(days=1))),
                    else_=literal(SEED_NOW + timedelta(days=30)),
                ),
                literal(SEED_NOW + timedelta(days=30)),
                literal(value=False),
                literal(SEED_NOW),
                sql_cast(
                    literal(AuthSessionAuthMethodEnum.PASSWORD.name),
                    AuthSessionModel.__table__.c.auth_method.type,
                ),
                literal("Chrome on Linux"),
                literal("Chrome"),
                literal("Linux"),
                sql_cast(
                    literal(AuthSessionDeviceTypeEnum.DESKTOP.name),
                    AuthSessionModel.__table__.c.user_agent_device.type,
                ),
            ).select_from(series),
        ),
    )


async def insert_tags(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    series = generate_series_subquery(end=profile.tag_count, name="tag_series")
    value = sql_cast(series.c.value, Integer)
    await connection.execute(
        insert(TagModel.__table__).from_select(
            ["id", "name_ru", "name_en", "slug"],
            select(
                hex_id_expr(value=value),
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
            ).select_from(series),
        ),
    )


async def insert_article_folders(*, connection: AsyncConnection) -> None:
    await connection.execute(
        insert(ArticleFolderModel.__table__).values(
            id=ARTICLE_FOLDER_ID,
            key="knowledge-base",
            name_ru="База знаний",
            name_en="Knowledge base",
            priority=1,
        ),
    )


async def insert_articles(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    series = generate_series_subquery(end=profile.article_count, name="article_series")
    value = sql_cast(series.c.value, Integer)
    target_article = func.mod(value, TARGET_ARTICLE_DIVISOR) == 0
    published_article = func.mod(value, 4) == 0
    await connection.execute(
        insert(ArticleModel.__table__).from_select(
            [
                "id",
                "title_ru",
                "title_en",
                "content_ru",
                "content_en",
                "slug",
                "folder_id",
                "author_username",
                "published_at",
                "publish_status",
            ],
            select(
                deterministic_hex_from_int(value=value),
                case(
                    (
                        target_article,
                        func.concat(literal("PostgreSQL полнотекстовый поиск "), value),
                    ),
                    else_=func.concat(literal("Статья "), value),
                ),
                case(
                    (target_article, func.concat(literal("PostgreSQL full text search "), value)),
                    else_=func.concat(literal("Engineering article "), value),
                ),
                case(
                    (
                        target_article,
                        func.concat(
                            literal("Проверка полнотекстовый поиск PostgreSQL для статьи "),
                            value,
                        ),
                    ),
                    else_=func.concat(literal("Общий backend материал "), value),
                ),
                case(
                    (
                        target_article,
                        func.concat(
                            literal("Benchmark content for PostgreSQL full text search article "),
                            value,
                        ),
                    ),
                    else_=func.concat(literal("General backend content "), value),
                ),
                func.concat(literal("article-"), value),
                literal(ARTICLE_FOLDER_ID),
                literal("benchmark"),
                case((published_article, literal(SEED_NOW)), else_=literal(None)),
                sql_cast(
                    case((published_article, literal("PUBLISHED")), else_=literal("DRAFT")),
                    ArticleModel.__table__.c.publish_status.type,
                ),
            ).select_from(series),
        ),
    )


async def insert_article_tag_links(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    target_link_count = min(
        profile.article_count // TARGET_ARTICLE_DIVISOR,
        profile.article_tag_link_count // TARGET_ARTICLE_DIVISOR,
    )
    general_link_count = profile.article_tag_link_count - target_link_count

    target_series = generate_series_subquery(end=target_link_count, name="target_links")
    target_value = sql_cast(target_series.c.value, Integer)
    target_select = select(
        deterministic_hex_from_int(value=target_value * TARGET_ARTICLE_DIVISOR),
        literal(hex_id(POSTGRESQL_ID)),
    ).select_from(target_series)

    general_series = generate_series_subquery(end=general_link_count, name="general_links")
    general_value = sql_cast(general_series.c.value, Integer)
    article_number = func.mod(general_value - 1, profile.article_count) + 1
    link_round = sql_cast((general_value - 1) / profile.article_count, Integer)
    tag_number = (
        func.mod(
            general_value + link_round * 9973,
            profile.tag_count - PYDANTIC_ID,
        )
        + GENERAL_TAG_START_ID
    )
    general_select = select(
        deterministic_hex_from_int(value=article_number),
        hex_id_expr(value=tag_number),
    ).select_from(general_series)

    await connection.execute(
        insert(ArticleToTagSecondaryModel.__table__).from_select(
            ["article_id", "tag_id"],
            union_all(target_select, general_select),
            include_defaults=False,
        ),
    )


async def insert_article_analytics(*, connection: AsyncConnection) -> None:
    await connection.execute(
        insert(ArticleDailyAnalyticsModel),
        [
            {
                "article_id": deterministic_python_hex_from_int(value=article_number),
                "date": recorded_on,
                "source_category": source_category,
                "view_count": 100 + article_number,
                "engaged_view_count": 10 + article_number,
            }
            for article_number in (100, 200)
            for recorded_on in (date(2026, 1, 14), date(2026, 1, 15))
            for source_category in (
                ArticleViewSourceCategory.DIRECT,
                ArticleViewSourceCategory.SEARCH,
            )
        ],
    )


async def insert_article_reactions(*, connection: AsyncConnection, profile: DatasetProfile) -> None:
    reaction_count = min(profile.article_count, ARTICLE_REACTION_SEED_COUNT)
    series = generate_series_subquery(end=reaction_count, name="article_reaction_series")
    value = sql_cast(series.c.value, Integer)
    article_number = func.mod(value - 1, profile.article_count) + 1
    await connection.execute(
        insert(ArticleReactionModel.__table__).from_select(
            [
                "article_id",
                "article_scoped_voter_hash",
                "reaction_kind",
                "created_at",
                "updated_at",
            ],
            select(
                deterministic_hex_from_int(value=article_number),
                func.rpad(
                    func.concat(literal("query-plan-voter-"), value),
                    64,
                    literal("x"),
                ),
                sql_cast(
                    case(
                        (func.mod(value, 2) == 0, literal(ArticleReactionKind.HEART.name)),
                        else_=literal(ArticleReactionKind.FIRE.name),
                    ),
                    ArticleReactionModel.__table__.c.reaction_kind.type,
                ),
                literal(SEED_NOW),
                literal(SEED_NOW),
            ).select_from(series),
            include_defaults=False,
        ),
    )


async def insert_resumes(*, connection: AsyncConnection) -> None:
    series = generate_series_subquery(end=RESUME_SEED_COUNT, name="resume_series")
    value = sql_cast(series.c.value, Integer)
    await connection.execute(
        insert(ResumeModel.__table__).from_select(
            ["id", "title", "language", "author_username", "content", "created_at", "updated_at"],
            select(
                hex_id_expr(value=value),
                func.concat(literal("Query plan resume "), value),
                sql_cast(literal(LanguageEnum.EN.name), ResumeModel.__table__.c.language.type),
                literal(SEED_USERNAME),
                literal(RESUME_SEED_CONTENT, type_=postgresql.JSONB),
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
                hex_id_expr(value=value),
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


async def insert_competency_matrix_structure(*, connection: AsyncConnection) -> None:
    sheet_series = generate_series_subquery(end=20, name="matrix_sheet_series")
    sheet_value = sql_cast(sheet_series.c.value, Integer)
    await connection.execute(
        insert(CompetencyMatrixSheetModel.__table__).from_select(
            ["id", "key", "name_ru", "name_en", "priority"],
            select(
                hex_id_expr(value=sheet_value),
                case(
                    (sheet_value == PYTHON_ID, literal("python")),
                    else_=func.concat(literal("sheet-"), sheet_value - 1),
                ),
                case(
                    (sheet_value == PYTHON_ID, literal("Питон")),
                    else_=func.concat(literal("Лист "), sheet_value - 1),
                ),
                case(
                    (sheet_value == PYTHON_ID, literal("Python")),
                    else_=func.concat(literal("Sheet "), sheet_value - 1),
                ),
                sheet_value,
            ).select_from(sheet_series),
        ),
    )

    section_series = generate_series_subquery(end=20 * 8, name="matrix_section_series")
    section_value = sql_cast(section_series.c.value, Integer)
    section_bucket = func.mod(section_value - 1, 8)
    section_sheet_number = sql_cast(func.floor((section_value - 1) / 8), Integer) + 1
    await connection.execute(
        insert(CompetencyMatrixSectionModel.__table__).from_select(
            ["id", "sheet_id", "name_ru", "name_en", "priority"],
            select(
                hex_id_expr(value=section_value),
                hex_id_expr(value=section_sheet_number),
                case(
                    (
                        sa_and(section_sheet_number == PYTHON_ID, section_bucket == 0),
                        literal("Основы"),
                    ),
                    else_=func.concat(literal("Раздел "), section_bucket),
                ),
                case(
                    (
                        sa_and(section_sheet_number == PYTHON_ID, section_bucket == 0),
                        literal("Basics"),
                    ),
                    else_=func.concat(literal("Section "), section_bucket),
                ),
                section_bucket + 1,
            ).select_from(section_series),
        ),
    )

    subsection_series = generate_series_subquery(end=20 * 8 * 12, name="matrix_subsection_series")
    subsection_value = sql_cast(subsection_series.c.value, Integer)
    subsection_bucket = func.mod(subsection_value - 1, 12)
    subsection_section_number = sql_cast(func.floor((subsection_value - 1) / 12), Integer) + 1
    subsection_sheet_number = sql_cast(func.floor((subsection_section_number - 1) / 8), Integer) + 1
    subsection_section_bucket = func.mod(subsection_section_number - 1, 8)
    python_basics = sa_and(
        subsection_sheet_number == PYTHON_ID,
        subsection_section_bucket == 0,
        subsection_bucket == 0,
    )
    await connection.execute(
        insert(CompetencyMatrixSubsectionModel.__table__).from_select(
            ["id", "section_id", "name_ru", "name_en", "priority"],
            select(
                hex_id_expr(value=subsection_value),
                hex_id_expr(value=subsection_section_number),
                case(
                    (python_basics, literal("Функции")),
                    else_=func.concat(literal("Подраздел "), subsection_bucket),
                ),
                case(
                    (python_basics, literal("Functions")),
                    else_=func.concat(literal("Subsection "), subsection_bucket),
                ),
                subsection_bucket + 1,
            ).select_from(subsection_series),
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
    draft_item = func.mod(value, 11) == 0
    missing_answer_en = func.mod(value, 13) == 0
    section_bucket = func.mod(value, 8)
    subsection_bucket = func.mod(value, 12)
    subsection_number = (sheet_bucket * 8 + section_bucket) * 12 + subsection_bucket + 1
    grade_bucket = func.mod(value, 5)
    frequency_bucket = func.mod(value, 5)
    await connection.execute(
        insert(CompetencyMatrixItemModel.__table__).from_select(
            [
                "id",
                "slug",
                "question_ru",
                "question_en",
                "question_ru_fingerprint",
                "question_en_fingerprint",
                "answer_ru",
                "answer_en",
                "interview_expected_answer_ru",
                "interview_expected_answer_en",
                "subsection_id",
                "grade",
                "interview_frequency",
                "suggested_by_username",
                "published_at",
                "publish_status",
            ],
            select(
                hex_id_expr(value=value),
                func.concat(literal("matrix-question-"), value),
                func.concat(literal("Вопрос матрицы "), value),
                func.concat(literal("Matrix question "), value),
                func.sha256(
                    func.convert_to(
                        func.concat(literal("вопрос матрицы "), value),
                        literal("UTF8"),
                    ),
                ),
                func.sha256(
                    func.convert_to(
                        func.concat(literal("matrix question "), value),
                        literal("UTF8"),
                    ),
                ),
                func.concat(literal("Ответ матрицы "), value),
                case(
                    (missing_answer_en, literal("")),
                    else_=func.concat(literal("Matrix answer "), value),
                ),
                func.concat(literal("Ожидаемый ответ "), value),
                func.concat(literal("Expected answer "), value),
                hex_id_expr(value=subsection_number),
                sql_cast(
                    case(
                        (grade_bucket == 0, literal("JUNIOR")),
                        (grade_bucket == 1, literal("JUNIOR_PLUS")),
                        (grade_bucket == MATRIX_GRADE_BUCKET_MIDDLE, literal("MIDDLE")),
                        (grade_bucket == MATRIX_GRADE_BUCKET_MIDDLE_PLUS, literal("MIDDLE_PLUS")),
                        else_=literal("SENIOR"),
                    ),
                    CompetencyMatrixItemModel.__table__.c.grade.type,
                ),
                sql_cast(
                    case(
                        (frequency_bucket == 0, literal("CONSTANTLY")),
                        (frequency_bucket == 1, literal("OFTEN")),
                        (frequency_bucket == MATRIX_FREQUENCY_BUCKET_RARELY, literal("RARELY")),
                        (
                            frequency_bucket == MATRIX_FREQUENCY_BUCKET_NEVER_SEEN,
                            literal("NEVER_SEEN"),
                        ),
                        else_=literal(None),
                    ),
                    CompetencyMatrixItemModel.__table__.c.interview_frequency.type,
                ),
                literal(SEED_USERNAME),
                case((draft_item, literal(None)), else_=literal(SEED_NOW)),
                sql_cast(
                    case((draft_item, literal("DRAFT")), else_=literal("PUBLISHED")),
                    CompetencyMatrixItemModel.__table__.c.publish_status.type,
                ),
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
            for item_id in (hex_id(100), hex_id(101))
            for resource_id in (hex_id(PYTHON_ID), hex_id(POSTGRESQL_ID))
        ],
    )


async def insert_queued_competency_matrix_questions(*, connection: AsyncConnection) -> None:
    await connection.execute(
        insert(QueuedQuestionModel.__table__),
        [
            {
                "id": hex_id(value),
                "question": f"Queued matrix question {value}",
                "question_fingerprint": CompetencyMatrixQuestionFingerprint.from_question(
                    question=f"Queued matrix question {value}",
                ).digest,
                "grade": "JUNIOR" if value % 5 == 0 else None,
                "sheet": "Python" if value % 7 == 0 else None,
                "section": "Basics" if value % 7 == 0 else None,
                "subsection": "Functions" if value % 7 == 0 else None,
                "suggested_by_username": SEED_USERNAME if value % 10 == 0 else "anon",
                "created_at": SEED_NOW + timedelta(seconds=value),
            }
            for value in range(1, QUEUED_QUESTION_SEED_COUNT + 1)
        ],
    )


async def insert_agent_access_records(*, connection: AsyncConnection) -> None:
    await connection.execute(
        insert(AgentClientModel.__table__),
        [
            {
                "id": hex_id(60_001 + value),
                "name": f"query-plan-agent-{value}",
                "status": AgentClientStatusEnum.ACTIVE,
                "scopes": [AgentScopeEnum.MATRIX_QUEUE_CLAIM],
                "created_at": SEED_NOW,
                "revoked_at": None,
            }
            for value in range(4)
        ],
    )
    await connection.execute(
        insert(AgentCertificateModel.__table__),
        [
            {
                "id": hex_id(62_001 + value),
                "agent_client_id": hex_id(60_001 + value),
                "fingerprint_sha256": f"{value + 1:064x}",
                "serial_number": f"query-plan-{value + 1}",
                "certificate_pem": "query-plan-certificate",
                "valid_from": SEED_NOW - timedelta(days=1),
                "expires_at": SEED_NOW + timedelta(days=14),
                "created_at": SEED_NOW - timedelta(days=1),
                "revoked_at": None,
            }
            for value in range(4)
        ]
        + [
            {
                "id": hex_id(62_011),
                "agent_client_id": hex_id(60_001),
                "fingerprint_sha256": f"{11:064x}",
                "serial_number": "query-plan-replacement",
                "certificate_pem": "query-plan-replacement-certificate",
                "valid_from": SEED_NOW,
                "expires_at": SEED_NOW + timedelta(days=90),
                "created_at": SEED_NOW,
                "revoked_at": None,
            },
        ],
    )
    await connection.execute(
        insert(MatrixQuestionClaimModel.__table__),
        [
            {
                "id": hex_id(61_001 + value),
                "agent_client_id": hex_id(60_001 + value),
                "queue_item_id": hex_id(100 + value),
                "claimed_at": SEED_NOW,
                "expires_at": SEED_NOW + timedelta(hours=2),
            }
            for value in range(2)
        ],
    )
    await connection.execute(
        insert(AgentCertificateRotationModel.__table__),
        [
            {
                "rotation_id": "query-plan-pending-rotation",
                "agent_client_id": hex_id(60_001),
                "current_certificate_id": hex_id(62_001),
                "replacement_certificate_id": hex_id(62_011),
                "csr_digest": "c" * 64,
                "created_at": SEED_NOW,
                "normal_access_until": SEED_NOW + timedelta(minutes=15),
                "confirmed_at": None,
            },
        ],
    )
    await connection.execute(
        insert(MatrixQuestionDraftCompletionModel.__table__),
        [
            {
                "claim_id": hex_id(63_001),
                "agent_client_id": hex_id(60_001),
                "queue_item_id": hex_id(100),
                "matrix_item_id": hex_id(100),
                "input_digest": "d" * 64,
                "completed_at": SEED_NOW,
            },
        ],
    )
    await connection.execute(
        insert(AgentAuditEventModel.__table__),
        [
            {
                "id": hex_id(64_001 + value),
                "agent_client_id": hex_id(60_001),
                "certificate_id": hex_id(62_001),
                "action": AgentActionEnum.GET_MATRIX_AUTHORING_CONTEXT,
                "queue_item_id": None,
                "matrix_item_id": None,
                "request_id": f"query-plan-audit-{value}",
                "result": AgentAuditResultEnum.SUCCESS,
                "input_digest": f"{value:064x}",
                "created_at": SEED_NOW - timedelta(days=value),
            }
            for value in range(365)
        ],
    )


def generate_series_subquery(*, end: int, name: str) -> Subquery:
    return select(func.generate_series(1, end).label("value")).subquery(name)


def deterministic_hex_from_int(*, value: object) -> object:
    return func.md5(sql_cast(value, String))


def deterministic_python_hex_from_int(*, value: int) -> str:
    return md5(str(value).encode(), usedforsecurity=False).hexdigest()


def hex_id_expr(*, value: object) -> object:
    return func.lpad(func.to_hex(value), 32, literal("0"))


def hex_id(value: int) -> str:
    return f"{value:032x}"


async def vacuum_analyze_seeded_tables(*, connection: AsyncConnection) -> None:
    stdout.write("Running VACUUM ANALYZE for seeded query-plan tables\n")
    for table_name in (
        "articles__article_model",
        "articles__tag_model",
        "articles__article_to_tag_secondary_model",
        "articles__article_daily_analytics_model",
        "articles__article_reaction_model",
        "resumes__resume_model",
        "auth__auth_session_model",
        "competency_matrix__external_resource_model",
        "competency_matrix__competency_matrix_item_model",
        "competency_matrix__resource_to_item_secondary_model",
        "competency_matrix__queued_question_model",
        "agent_access__agent_client_model",
        "agent_access__agent_certificate_model",
        "agent_access__agent_certificate_rotation_model",
        "agent_access__matrix_question_claim_model",
        "agent_access__matrix_question_draft_completion_model",
        "agent_access__agent_audit_event_model",
        "auth__user_model",
    ):
        await connection.execute(text(f"VACUUM ANALYZE {table_name}"))
