import sqlalchemy as sa
from alembic import op
from sqlalchemy_dev_utils.mixins.audit import (
    get_updated_at_ddl_statement,
    get_updated_at_trigger_query,
    get_drop_update_at_trigger_query,
)
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "blog_posts",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("published_at", UTCDateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "PUBLISHED", name="statusenum", native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            UTCDateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            UTCDateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.execute(get_updated_at_ddl_statement(column_name="updated_at"))
    op.execute(get_updated_at_trigger_query(table_name="blog_posts", column_name="updated_at"))


def downgrade() -> None:
    op.drop_table("blog_posts")
    op.execute(get_drop_update_at_trigger_query(table_name="blog_posts", column_name="updated_at"))
