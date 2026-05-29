from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.schemas import User
from core.competency_matrix.schemas import CompetencyMatrixItem, ExternalResource
from core.contacts.exceptions import ContactMeRequestNotFoundError
from core.contacts.schemas import ContactMe
from core.notes.schemas import Note, Tag
from infra.postgresql.models import (
    CompetencyMatrixItemModel,
    ContactMeModel,
    ExternalResourceModel,
    NoteModel,
    NoteToTagSecondaryModel,
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
        model = CompetencyMatrixItemModel.from_domain_schema(item=item, include_relationships=True)
        await self.session.merge(model)
        await self.session.flush()
        return model

    async def create_competency_matrix_items(
        self,
        items: list[CompetencyMatrixItem],
    ) -> list[CompetencyMatrixItemModel]:
        db_items = [
            CompetencyMatrixItemModel.from_domain_schema(item=item, include_relationships=True)
            for item in items
        ]
        self.session.add_all(db_items)
        await self.session.flush()
        return db_items

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

    async def create_note(self, note: Note) -> NoteModel:
        db_note = NoteModel.from_domain_schema(note=note)
        db_note.tag_links = [
            NoteToTagSecondaryModel.from_domain_schema(tag=tag) for tag in note.tags
        ]
        self.session.add(db_note)
        await self.session.flush()
        return db_note

    async def create_notes(self, notes: list[Note]) -> list[NoteModel]:
        db_notes = []
        for note in notes:
            db_note = NoteModel.from_domain_schema(note=note)
            db_note.tag_links = [
                NoteToTagSecondaryModel.from_domain_schema(tag=tag) for tag in note.tags
            ]
            db_notes.append(db_note)
        self.session.add_all(db_notes)
        await self.session.flush()
        return db_notes

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
