import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

RESUME_TABLE = "resumes__resume_model"


def upgrade() -> None:
    op.drop_index("resumes_resume_updated_id_idx", table_name=RESUME_TABLE)
    op.add_column(
        RESUME_TABLE,
        sa.Column("author_username", sa.String(length=255), nullable=False),
    )
    op.create_index(
        "resumes_resume_author_updated_id_idx",
        RESUME_TABLE,
        ["author_username", sa.text("updated_at DESC"), sa.text("id DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("resumes_resume_author_updated_id_idx", table_name=RESUME_TABLE)
    op.drop_column(RESUME_TABLE, "author_username")
    op.create_index(
        "resumes_resume_updated_id_idx",
        RESUME_TABLE,
        [sa.text("updated_at DESC"), sa.text("id DESC")],
        unique=False,
    )
