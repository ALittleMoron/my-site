import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None

USER_TABLE = "auth__user_model"


def upgrade() -> None:
    op.add_column(
        USER_TABLE,
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.alter_column(USER_TABLE, "is_active", server_default=None)
    op.create_index(
        "users_username_lower_uniq",
        USER_TABLE,
        [sa.func.lower(sa.column("username")).label("username_lower")],
        unique=True,
    )
    op.create_index(
        "users_managed_accounts_list_idx",
        USER_TABLE,
        [
            "role",
            sa.func.lower(sa.column("username")).label("username_lower"),
            "username",
        ],
    )
    op.create_index(
        "users_single_owner_uniq",
        USER_TABLE,
        ["role"],
        unique=True,
        postgresql_where=sa.column("role") == "OWNER",
    )


def downgrade() -> None:
    op.drop_index("users_single_owner_uniq", table_name=USER_TABLE)
    op.drop_index("users_managed_accounts_list_idx", table_name=USER_TABLE)
    op.drop_index("users_username_lower_uniq", table_name=USER_TABLE)
    op.drop_column(USER_TABLE, "is_active")
