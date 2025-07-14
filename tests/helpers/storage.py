from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.competency_matrix.schemas import CompetencyMatrixItem
from core.contacts.exceptions import ContactMePurchaseNotFoundError
from core.contacts.schemas import ContactMe
from core.users.schemas import User
from db.models import CompetencyMatrixItemModel, UserModel, ContactMeModel


@dataclass(kw_only=True)
class StorageHelper:
    session: AsyncSession

    async def get_contact_me_by_id(self, contact_me_id: UUID) -> ContactMe:
        query = select(ContactMeModel).where(ContactMeModel.id == contact_me_id)
        contact_me = await self.session.scalar(query)
        if contact_me is None:
            raise ContactMePurchaseNotFoundError
        return contact_me.to_schema()

    async def create_competency_matrix_item(
        self,
        item: CompetencyMatrixItem,
    ) -> CompetencyMatrixItemModel:
        model = CompetencyMatrixItemModel.from_domain_schema(item=item)
        await self.session.merge(model)
        return model

    async def create_competency_matrix_items(
        self,
        items: list[CompetencyMatrixItem],
    ) -> list[CompetencyMatrixItemModel]:
        db_items = [CompetencyMatrixItemModel.from_domain_schema(item=item) for item in items]
        self.session.add_all(db_items)
        await self.session.commit()
        return db_items

    async def create_user(self, user: User) -> UserModel:
        model = UserModel.from_domain_schema(schema=user)
        await self.session.merge(model)
        return model

    async def create_users(self, users: list[User]) -> list[UserModel]:
        db_users = [UserModel.from_domain_schema(schema=user) for user in users]
        self.session.add_all(db_users)
        await self.session.commit()
        return db_users
