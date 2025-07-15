import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mentoring_contact_me",
        sa.Column("user_ip", sa.String(length=45), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("telegram", sa.String(length=256), nullable=True),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("mentoring_contact_me")
