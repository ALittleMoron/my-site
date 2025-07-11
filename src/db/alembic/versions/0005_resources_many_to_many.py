import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "resource_to_item_secondary",
        sa.Column("item_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "resource_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["item_id"], ["competency_matrix_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["resource_id"], ["competency_matrix_resources.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_constraint(
        op.f("fk_competency_matrix_resources_item_id"),
        "competency_matrix_resources",
        type_="foreignkey",
    )
    op.drop_column("competency_matrix_resources", "item_id")


def downgrade() -> None:
    op.add_column(
        "competency_matrix_resources",
        sa.Column(
            "item_id",
            sa.BIGINT(),
            autoincrement=False,
            nullable=False,
            server_default="0",
        ),
    )
    op.execute("DELETE FROM competency_matrix_resources WHERE item_id = 0")
    op.alter_column(
        "competency_matrix_resources",
        "item_id",
        server_default=None,
    )
    op.create_foreign_key(
        op.f("fk_competency_matrix_resources_item_id"),
        "competency_matrix_resources",
        "competency_matrix_items",
        ["item_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_table("resource_to_item_secondary")
