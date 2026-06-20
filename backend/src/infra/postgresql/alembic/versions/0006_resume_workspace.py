import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

RESUME_TABLE = "resumes__resume_model"


def upgrade() -> None:
    op.create_table(
        RESUME_TABLE,
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=2), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
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
    )
    op.create_index(
        "resumes_resume_updated_id_idx",
        RESUME_TABLE,
        [sa.text("updated_at DESC"), sa.text("id DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("resumes_resume_updated_id_idx", table_name=RESUME_TABLE)
    op.drop_table(RESUME_TABLE)
