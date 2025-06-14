import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("competency_matrix_items", "status_changed")


def downgrade() -> None:
    op.add_column(
        "competency_matrix_items",
        sa.Column(
            "status_changed",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.alter_column(
        "competency_matrix_items",
        "status_changed",
        server_default=None,  # type: ignore
    )
