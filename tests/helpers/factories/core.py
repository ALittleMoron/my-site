import uuid
from datetime import datetime, UTC
from typing import Any

from core.auth.enums import RoleEnum
from core.auth.schemas import User, JwtUser
from core.auth.types import Token
from core.blog.schemas import BlogPost, BlogPostList
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItems,
    ExternalResource,
    Sheets,
    ExternalResources,
    CompetencyMatrixItemUpsertParams,
)
from core.contacts.schemas import ContactMe
from core.enums import PublishStatusEnum
from core.files.schemas import PresignPutObjectParams, PresignPutObject
from core.files.types import Namespace
from core.schemas import Secret
from core.types import IntId, SearchName


class CoreFactoryHelper:
    @classmethod
    def external_resource(
        cls,
        resource_id: int,
        name: str = "RESOURCE",
        url: str = "https://example.com",
        context: str = "Context",
    ) -> ExternalResource:
        return ExternalResource(
            id=cls.int_id(resource_id),
            name=name,
            url=url,
            context=context,
        )

    @classmethod
    def external_resources(
        cls,
        values: list[ExternalResource] | None = None,
    ) -> ExternalResources:
        return ExternalResources(values=values or [])

    @classmethod
    def competency_matrix_item(
        cls,
        item_id: int,
        question: str = "QUESTION",
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        answer: str = "Answer",
        interview_expected_answer: str = "Answer",
        sheet: str = "Sheet",
        grade: str = "Junior",
        section: str = "Section",
        subsection: str = "Subsection",
        resources: list[ExternalResource] | None = None,
    ) -> CompetencyMatrixItem:
        return CompetencyMatrixItem(
            id=cls.int_id(item_id),
            question=question,
            publish_status=publish_status,
            answer=answer,
            interview_expected_answer=interview_expected_answer,
            sheet=sheet,
            grade=grade,
            section=section,
            subsection=subsection,
            resources=ExternalResources(values=resources or []),
        )

    @classmethod
    def competency_matrix_item_upsert_params(
        cls,
        item_id: int,
        question: str = "QUESTION",
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        answer: str = "Answer",
        interview_expected_answer: str = "Answer",
        sheet: str = "Sheet",
        grade: str = "Junior",
        section: str = "Section",
        subsection: str = "Subsection",
        resources: list[IntId | ExternalResource] | None = None,
    ) -> CompetencyMatrixItemUpsertParams:
        return CompetencyMatrixItemUpsertParams(
            id=cls.int_id(item_id),
            question=question,
            publish_status=publish_status,
            answer=answer,
            interview_expected_answer=interview_expected_answer,
            sheet=sheet,
            grade=grade,
            section=section,
            subsection=subsection,
            resources=resources or [],
        )

    @classmethod
    def sheets(cls, values: list[str] | None = None) -> Sheets:
        return Sheets(values=values or [])

    @classmethod
    def user(
        cls,
        username: str = "",
        password_hash: str = "",
        role: RoleEnum = RoleEnum.USER,
    ) -> User:
        return User(username=username, password_hash=Secret(password_hash), role=role)

    @classmethod
    def competency_matrix_items(
        cls,
        values: list[CompetencyMatrixItem] | None = None,
    ) -> CompetencyMatrixItems:
        return CompetencyMatrixItems(values=values or [])

    @classmethod
    def contact_me(
        cls,
        contact_me_id: uuid.UUID | None = None,
        name: str | None = None,
        email: str | None = None,
        telegram: str | None = None,
        message: str = "Message",
    ) -> ContactMe:
        return ContactMe(
            id=contact_me_id or uuid.uuid4(),
            name=name,
            email=email,
            telegram=telegram,
            message=message,
        )

    @classmethod
    def blog_post(
        cls,
        post_id: uuid.UUID | None = None,
        title: str = "Test Blog Post",
        content: str = "This is a test blog post content.",
        slug: str = "test-blog-post",
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        published_at: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> BlogPost:
        now = datetime.now(tz=UTC)
        return BlogPost(
            id=post_id or uuid.uuid4(),
            title=title,
            content=content,
            slug=slug,
            publish_status=publish_status,
            published_at=(
                datetime.fromisoformat(published_at).replace(tzinfo=UTC)
                if published_at is not None
                else None
            ),
            created_at=(
                datetime.fromisoformat(created_at).replace(tzinfo=UTC)
                if created_at is not None
                else now
            ),
            updated_at=(
                datetime.fromisoformat(updated_at).replace(tzinfo=UTC)
                if updated_at is not None
                else now
            ),
        )

    @classmethod
    def blog_post_list(
        cls,
        posts: list[BlogPost] | None = None,
        total_count: int = 0,
        total_pages: int = 0,
    ) -> BlogPostList:
        return BlogPostList(posts=posts or [], total_count=total_count, total_pages=total_pages)

    @classmethod
    def jwt_user(
        cls,
        username: str = "test",
        role: RoleEnum = RoleEnum.ADMIN,
    ) -> JwtUser:
        return JwtUser(username=username, role=role)

    @classmethod
    def presign_put_object_params(
        cls,
        folder: str = "folder",
        namespace: Namespace = "media",
        content_type: str = "application/octet-stream",
    ) -> PresignPutObjectParams:
        return PresignPutObjectParams(
            folder=folder,
            namespace=namespace,
            content_type=content_type,
        )

    @classmethod
    def presign_put_object(
        cls,
        upload_url: str = "http://localhost/upload_url",
        access_url: str = "http://localhost/access_url",
    ) -> PresignPutObject:
        return PresignPutObject(upload_url=upload_url, access_url=access_url)

    @classmethod
    def token(cls, value: bytes) -> Token:
        return Token(value)

    @classmethod
    def int_id(cls, value: int) -> IntId:
        return IntId(value)

    @classmethod
    def search_name(cls, value: Any) -> SearchName:
        return SearchName(value)
