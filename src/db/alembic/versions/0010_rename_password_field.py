from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("users", "password", new_column_name="password_hash")


def downgrade() -> None:
    op.alter_column("users", "password_hash", new_column_name="password")
