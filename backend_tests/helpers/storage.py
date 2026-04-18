from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.schemas import User
from core.blog.schemas import BlogPost
from core.competency_matrix.schemas import CompetencyMatrixItem, ExternalResource
from core.contacts.exceptions import ContactMeRequestNotFoundError
from core.contacts.schemas import ContactMe
from db.models import (
    CompetencyMatrixItemModel,
    UserModel,
    ContactMeModel,
    BlogPostModel,
    ExternalResourceModel,
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
        model = CompetencyMatrixItemModel.from_domain_schema(item=item)
        await self.session.merge(model)
        await self.session.flush()
        return model

    async def create_competency_matrix_items(
        self,
        items: list[CompetencyMatrixItem],
    ) -> list[CompetencyMatrixItemModel]:
        db_items = [CompetencyMatrixItemModel.from_domain_schema(item=item) for item in items]
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

    async def create_blog_post(self, blog_post: BlogPost) -> BlogPostModel:
        db_blog_post = BlogPostModel.from_domain_schema(post=blog_post)
        self.session.add(db_blog_post)
        await self.session.flush()
        return db_blog_post

    async def create_blog_posts(self, blog_posts: list[BlogPost]) -> list[BlogPostModel]:
        db_blog_posts = [BlogPostModel.from_domain_schema(post=post) for post in blog_posts]
        self.session.add_all(db_blog_posts)
        await self.session.flush()
        return db_blog_posts

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
