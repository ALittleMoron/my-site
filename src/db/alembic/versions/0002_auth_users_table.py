import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=127), nullable=False),
        sa.Column(
            "role",
            sa.Enum("USER", "ADMIN", name="roleenum", native_enum=False, length=10),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("username"),
    )
    op.create_index(
        "users_username_idx",
        "users",
        ["username"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("users_username_idx", table_name="users")
    op.drop_table("users")
