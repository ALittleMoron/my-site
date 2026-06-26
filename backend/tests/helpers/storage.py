from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.articles.schemas import Article, Tag
from core.auth.schemas import User
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItemStructure,
    ExternalResource,
    QueuedCompetencyMatrixQuestion,
)
from core.contacts.exceptions import ContactMeRequestNotFoundError
from core.contacts.schemas import ContactMe
from infra.postgresql.models import (
    ArticleModel,
    ArticleToTagSecondaryModel,
    CompetencyMatrixItemModel,
    CompetencyMatrixSectionModel,
    CompetencyMatrixSheetModel,
    CompetencyMatrixSubsectionModel,
    ContactMeModel,
    ExternalResourceModel,
    QueuedQuestionModel,
    TagModel,
    UserModel,
)


@dataclass(kw_only=True)
class StorageHelper:
    session: AsyncSession

    async def get_contact_me_by_id(self, contact_me_id: UUID) -> ContactMe:
        query = select(ContactMeModel).where(ContactMeModel.id == contact_me_id)
        contact_me = await self.session.scalar(query)
        if contact_me is None:
            raise ContactMeRequestNotFoundError
        return contact_me.to_domain_schema()

    async def create_competency_matrix_item(
        self,
        item: CompetencyMatrixItem,
    ) -> CompetencyMatrixItemModel:
        await self.create_competency_matrix_structure(structure=item.structure)
        model = CompetencyMatrixItemModel.from_domain_schema(item=item, include_relationships=True)
        await self.session.merge(model)
        await self.session.flush()
        return model

    async def create_competency_matrix_items(
        self,
        items: list[CompetencyMatrixItem],
    ) -> list[CompetencyMatrixItemModel]:
        for item in items:
            await self.create_competency_matrix_structure(structure=item.structure)
        db_items = [
            CompetencyMatrixItemModel.from_domain_schema(item=item, include_relationships=True)
            for item in items
        ]
        self.session.add_all(db_items)
        await self.session.flush()
        return db_items

    async def create_competency_matrix_structure(
        self,
        structure: CompetencyMatrixItemStructure,
    ) -> None:
        await self._ensure_matrix_sheet(structure=structure)
        await self._ensure_matrix_section(structure=structure)
        await self._ensure_matrix_subsection(structure=structure)
        await self.session.flush()
        await self._sync_competency_matrix_structure_sequences()

    async def _ensure_matrix_sheet(self, structure: CompetencyMatrixItemStructure) -> None:
        sheet = await self.session.get(CompetencyMatrixSheetModel, structure.sheet_id)
        if sheet is None:
            self.session.add(
                CompetencyMatrixSheetModel(
                    id=structure.sheet_id,
                    key=structure.sheet_key,
                    name_ru=structure.sheet_ru,
                    name_en=structure.sheet_en,
                ),
            )
            return
        expected = (structure.sheet_key, structure.sheet_ru, structure.sheet_en)
        actual = (sheet.key, sheet.name_ru, sheet.name_en)
        if actual != expected:
            msg = (
                f"Conflicting matrix sheet fixture id {structure.sheet_id}: {actual} != {expected}"
            )
            raise AssertionError(msg)

    async def _ensure_matrix_section(self, structure: CompetencyMatrixItemStructure) -> None:
        section = await self.session.get(CompetencyMatrixSectionModel, structure.section_id)
        if section is None:
            self.session.add(
                CompetencyMatrixSectionModel(
                    id=structure.section_id,
                    sheet_id=structure.sheet_id,
                    name_ru=structure.section_ru,
                    name_en=structure.section_en,
                ),
            )
            return
        expected = (structure.sheet_id, structure.section_ru, structure.section_en)
        actual = (section.sheet_id, section.name_ru, section.name_en)
        if actual != expected:
            msg = (
                f"Conflicting matrix section fixture id {structure.section_id}: "
                f"{actual} != {expected}"
            )
            raise AssertionError(msg)

    async def _ensure_matrix_subsection(self, structure: CompetencyMatrixItemStructure) -> None:
        subsection = await self.session.get(
            CompetencyMatrixSubsectionModel,
            structure.subsection_id,
        )
        if subsection is None:
            self.session.add(
                CompetencyMatrixSubsectionModel(
                    id=structure.subsection_id,
                    section_id=structure.section_id,
                    name_ru=structure.subsection_ru,
                    name_en=structure.subsection_en,
                ),
            )
            return
        expected = (structure.section_id, structure.subsection_ru, structure.subsection_en)
        actual = (subsection.section_id, subsection.name_ru, subsection.name_en)
        if actual != expected:
            msg = (
                f"Conflicting matrix subsection fixture id {structure.subsection_id}: "
                f"{actual} != {expected}"
            )
            raise AssertionError(msg)

    async def _sync_competency_matrix_structure_sequences(self) -> None:
        for model in (
            (CompetencyMatrixSheetModel, "competency_matrix__competency_matrix_sheet_model"),
            (CompetencyMatrixSectionModel, "competency_matrix__competency_matrix_section_model"),
            (
                CompetencyMatrixSubsectionModel,
                "competency_matrix__competency_matrix_subsection_model",
            ),
        ):
            model_class, table_name = model
            max_id = await self.session.scalar(select(func.max(model_class.id)))
            if max_id is None:
                continue
            await self.session.execute(
                select(
                    func.setval(
                        func.pg_get_serial_sequence(table_name, "id"),
                        max_id,
                    ),
                ),
            )

    async def create_queued_matrix_questions(
        self,
        questions: list[QueuedCompetencyMatrixQuestion],
    ) -> list[QueuedQuestionModel]:
        db_questions = [
            QueuedQuestionModel.from_domain_schema(schema=question) for question in questions
        ]
        self.session.add_all(db_questions)
        await self.session.flush()
        return db_questions

    async def create_user(self, user: User) -> UserModel:
        model = UserModel.from_domain_schema(schema=user)
        await self.session.merge(model)
        await self.session.flush()
        return model

    async def create_users(self, users: list[User]) -> list[UserModel]:
        db_users = [UserModel.from_domain_schema(schema=user) for user in users]
        self.session.add_all(db_users)
        await self.session.flush()
        return db_users

    async def create_article(self, article: Article) -> ArticleModel:
        db_article = ArticleModel.from_domain_schema(article=article)
        db_article.tag_links = [
            ArticleToTagSecondaryModel.from_domain_schema(tag=tag) for tag in article.tags
        ]
        self.session.add(db_article)
        await self.session.flush()
        return db_article

    async def create_articles(self, articles: list[Article]) -> list[ArticleModel]:
        db_articles = []
        for article in articles:
            db_article = ArticleModel.from_domain_schema(article=article)
            db_article.tag_links = [
                ArticleToTagSecondaryModel.from_domain_schema(tag=tag) for tag in article.tags
            ]
            db_articles.append(db_article)
        self.session.add_all(db_articles)
        await self.session.flush()
        return db_articles

    async def create_tag(self, tag: Tag) -> TagModel:
        db_tag = TagModel.from_domain_schema(tag=tag)
        self.session.add(db_tag)
        await self.session.flush()
        return db_tag

    async def create_tags(self, tags: list[Tag]) -> list[TagModel]:
        db_tags = [TagModel.from_domain_schema(tag=tag) for tag in tags]
        self.session.add_all(db_tags)
        await self.session.flush()
        return db_tags

    async def create_external_resource(self, resource: ExternalResource) -> ExternalResourceModel:
        db_resource_model = ExternalResourceModel.from_domain_schema(schema=resource)
        self.session.add(db_resource_model)
        await self.session.flush()
        return db_resource_model

    async def create_external_resources(
        self,
        resources: list[ExternalResource],
    ) -> list[ExternalResourceModel]:
        db_resource_models = [
            ExternalResourceModel.from_domain_schema(schema=resource) for resource in resources
        ]
        self.session.add_all(db_resource_models)
        await self.session.flush()
        return db_resource_models
