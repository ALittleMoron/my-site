from typing import Self

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_dev_utils.mixins.audit import AuditMixin
from sqlalchemy_dev_utils.mixins.ids import UUIDMixin

from core.blog.schemas import BlogPost
from db.models.mixins.publish import PublishMixin


class BlogPostModel(PublishMixin, UUIDMixin, AuditMixin):
    __tablename__ = "blog_posts"

    title: Mapped[str] = mapped_column(
        String(length=255),
        doc="Title of the blog post",
    )
    content: Mapped[str] = mapped_column(
        String(),
        doc="Content of the blog post",
    )
    slug: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        doc="URL slug for the blog post",
    )

    def __str__(self) -> str:
        return f'Blog post "{self.title}"'

    @classmethod
    def from_schema(cls, post: BlogPost) -> Self:
        return cls(
            id=post.id,
            title=post.title,
            content=post.content,
            slug=post.slug,
            published_at=post.published_at,
            publish_status=post.publish_status,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

    def to_schema(self) -> BlogPost:
        return BlogPost(
            id=self.id,
            title=self.title,
            content=self.content,
            slug=self.slug,
            published_at=self.published_at,
            publish_status=self.publish_status,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
