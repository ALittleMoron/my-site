from datetime import UTC, date, datetime

import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy.engine import Connection

from core.articles.enums import ArticleReactionKind, ArticleViewSourceCategory
from core.competency_matrix.enums import GradeEnum
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.resumes.schemas import ResumeCreateParams
from infra.postgresql.models import (
    ArticleDailyAnalyticsModel,
    ArticleFolderModel,
    ArticleModel,
    ArticleReactionModel,
    ArticleToTagSecondaryModel,
    CompetencyMatrixItemModel,
    CompetencyMatrixSectionModel,
    CompetencyMatrixSheetModel,
    CompetencyMatrixSubsectionModel,
    ContactMeModel,
    ExternalResourceModel,
    QueuedQuestionModel,
    ResumeModel,
    TagModel,
)
from infra.postgresql.models.competency_matrix import ResourceToItemSecondaryModel
from tests.test_cases import StorageTestCase

ID_TABLES = (
    "articles__article_folder_model",
    "articles__article_model",
    "articles__tag_model",
    "articles__article_to_tag_secondary_model",
    "articles__article_daily_analytics_model",
    "articles__article_reaction_model",
    "contacts__contact_me_model",
    "resumes__resume_model",
    "competency_matrix__competency_matrix_sheet_model",
    "competency_matrix__competency_matrix_section_model",
    "competency_matrix__competency_matrix_subsection_model",
    "competency_matrix__competency_matrix_item_model",
    "competency_matrix__external_resource_model",
    "competency_matrix__queued_question_model",
    "competency_matrix__resource_to_item_secondary_model",
)


class TestHexUuidIdDefaults(StorageTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.now = datetime(2026, 7, 2, 12, 0, tzinfo=UTC)

    async def test_orm_defaults_generate_hex_ids_when_constructors_omit_ids(self) -> None:
        article = ArticleModel(
            title_ru="Статья",
            title_en="Article",
            content_ru="Контент",
            content_en="Content",
            slug="hex-default-article",
            folder=ArticleFolderModel(
                key="hex-default-folder",
                name_ru="Общее",
                name_en="General",
                priority=1,
            ),
            author_username="admin",
            publish_status=PublishStatusEnum.PUBLISHED,
            published_at=self.now,
        )
        tag = TagModel(name_ru="Python", name_en="Python", slug="hex-default-tag")
        article_tag = ArticleToTagSecondaryModel(article=article, tag=tag)
        analytics = ArticleDailyAnalyticsModel(
            article=article,
            date=date(2026, 7, 2),
            source_category=ArticleViewSourceCategory.DIRECT,
            view_count=1,
            engaged_view_count=1,
        )
        reaction = ArticleReactionModel(
            article=article,
            article_scoped_voter_hash="a" * 64,
            reaction_kind=ArticleReactionKind.HEART,
        )
        contact = ContactMeModel(
            name="Dmitriy",
            email="dmitriy@example.com",
            telegram="@dmitriy",
            message="Hello",
        )
        resume = ResumeModel.from_create_params(
            params=ResumeCreateParams(
                title="Backend resume",
                language=LanguageEnum.EN,
                author_username="admin",
                content=self.factory.core.resume_content(),
            ),
        )
        sheet = CompetencyMatrixSheetModel(
            key="hex-default-sheet",
            name_ru="Лист",
            name_en="Sheet",
            priority=1,
        )
        section = CompetencyMatrixSectionModel(
            sheet=sheet,
            name_ru="Секция",
            name_en="Section",
            priority=1,
        )
        subsection = CompetencyMatrixSubsectionModel(
            section=section,
            name_ru="Подсекция",
            name_en="Subsection",
            priority=1,
        )
        item = CompetencyMatrixItemModel(
            slug="hex-default-question",
            question_ru="Вопрос",
            question_en="Question",
            answer_ru="Ответ",
            answer_en="Answer",
            interview_expected_answer_ru="Ожидаемый ответ",
            interview_expected_answer_en="Expected answer",
            subsection=subsection,
            publish_status=PublishStatusEnum.DRAFT,
            grade=GradeEnum.JUNIOR,
            interview_frequency=None,
        )
        resource = ExternalResourceModel(
            name_ru="Ресурс",
            name_en="Resource",
            url="https://example.com/hex-default-resource",
        )
        resource_link = ResourceToItemSecondaryModel(
            item=item,
            resource=resource,
            context_ru="Контекст",
            context_en="Context",
        )
        queued_question = QueuedQuestionModel(
            question="What is a UUID hex id?",
            grade=GradeEnum.JUNIOR,
            sheet="Python",
            section=None,
            subsection=None,
            suggested_by_username=None,
            created_at=self.now,
        )

        self.db_session.add_all(
            [
                article,
                tag,
                article_tag,
                analytics,
                reaction,
                contact,
                resume,
                sheet,
                section,
                subsection,
                item,
                resource,
                resource_link,
                queued_question,
            ],
        )
        await self.db_session.flush()

        generated_ids = (
            article.folder.id,
            article.id,
            tag.id,
            article_tag.id,
            analytics.id,
            reaction.id,
            contact.id,
            resume.id,
            sheet.id,
            section.id,
            subsection.id,
            item.id,
            resource.id,
            resource_link.id,
            queued_question.id,
        )
        for generated_id in generated_ids:
            self.asserts.hex_id(generated_id)
        assert len(set(generated_ids)) == len(generated_ids)
        assert article_tag.article_id == article.id
        assert article_tag.tag_id == tag.id
        assert analytics.article_id == article.id
        assert reaction.article_id == article.id
        assert section.sheet_id == sheet.id
        assert subsection.section_id == section.id
        assert item.subsection_id == subsection.id
        assert resource_link.item_id == item.id
        assert resource_link.resource_id == resource.id

    async def test_id_columns_have_database_server_defaults(self) -> None:
        connection = await self.db_session.connection()
        defaults = await connection.run_sync(_id_column_defaults)

        assert set(defaults) == set(ID_TABLES)
        assert all(default is not None for default in defaults.values())
        assert all("gen_random_uuid" in str(default) for default in defaults.values())


def _id_column_defaults(connection: Connection) -> dict[str, str | None]:
    inspector = sa.inspect(connection)
    return {
        table_name: next(
            column["default"]
            for column in inspector.get_columns(table_name)
            if column["name"] == "id"
        )
        for table_name in ID_TABLES
    }
