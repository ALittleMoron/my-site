import uuid
from datetime import datetime, UTC

from core.blog.schemas import BlogPost, BlogPostList
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    CompetencyMatrixItems,
    ExternalResource,
    Sheets,
    ExternalResources,
)
from core.contacts.schemas import ContactMe
from core.enums import StatusEnum
from core.schemas import Secret
from core.users.schemas import User, RoleEnum


class CoreFactoryHelper:
    @classmethod
    def resource(
        cls,
        resource_id: int,
        name: str = "RESOURCE",
        url: str = "https://example.com",
        context: str = "Context",
    ) -> ExternalResource:
        return ExternalResource(
            id=resource_id,
            name=name,
            url=url,
            context=context,
        )

    @classmethod
    def competency_matrix_item(
        cls,
        item_id: int,
        question: str,
        status: StatusEnum = StatusEnum.PUBLISHED,
        answer: str = "",
        interview_expected_answer: str = "",
        sheet: str = "",
        grade: str = "",
        section: str = "",
        subsection: str = "",
        resources: list[ExternalResource] | None = None,
    ) -> CompetencyMatrixItem:
        return CompetencyMatrixItem(
            id=item_id,
            question=question,
            status=status,
            answer=answer,
            interview_expected_answer=interview_expected_answer,
            sheet=sheet,
            grade=grade,
            section=section,
            subsection=subsection,
            resources=ExternalResources(values=resources or []),
        )

    @classmethod
    def sheets(cls, values: list[str] | None = None) -> Sheets:
        return Sheets(values=values or [])

    @classmethod
    def user(
        cls,
        username: str = "",
        password: str = "",
        role: RoleEnum = RoleEnum.USER,
    ) -> User:
        return User(
            username=username,
            password=Secret(password),
            role=role,
        )

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
        user_ip: str = "127.0.0.1",
        name: str | None = None,
        email: str | None = None,
        telegram: str | None = None,
        message: str = "Message",
    ) -> ContactMe:
        return ContactMe(
            id=contact_me_id or uuid.uuid4(),
            user_ip=user_ip,
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
        status: StatusEnum = StatusEnum.PUBLISHED,
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
            status=status,
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
        return BlogPostList(
            posts=posts or [],
            total_count=total_count,
            total_pages=total_pages,
        )
