import sqlalchemy as sa
from alembic import op
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "competency_matrix_items",
        sa.Column(
            "published_at",
            UTCDateTime(timezone=True),
            nullable=True,
        ),
    )
    op.execute("UPDATE competency_matrix_items SET published_at = NOW() WHERE status = 'PUBLISHED'")
    op.alter_column(
        "competency_matrix_items",
        "status",
        new_column_name="publish_status",
    )
    op.alter_column(
        "blog_posts",
        "status",
        new_column_name="publish_status",
    )


def downgrade() -> None:
    op.alter_column(
        "competency_matrix_items",
        "publish_status",
        new_column_name="status",
    )
    op.alter_column(
        "blog_posts",
        "publish_status",
        new_column_name="status",
    )
    op.drop_column("competency_matrix_items", "published_at")
