import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("mentoring_contact_me", "user_ip")


def downgrade() -> None:
    op.add_column(
        "mentoring_contact_me",
        sa.Column("user_ip", sa.VARCHAR(length=45), autoincrement=False, nullable=False),
    )
