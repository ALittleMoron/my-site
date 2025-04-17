import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("competency_matrix_item_to_resource")
    op.add_column(
        "competency_matrix_resources",
        sa.Column(
            "item_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_competency_matrix_resources_item_id",
        "competency_matrix_resources",
        "competency_matrix_items",
        ["item_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_competency_matrix_resources_item_id",
        "competency_matrix_resources",
        type_="foreignkey",
    )
    op.drop_column("competency_matrix_resources", "item_id")
    op.create_table(
        "competency_matrix_item_to_resource",
        sa.Column("resource_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("item_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["competency_matrix_items.id"],
            name="competency_matrix_item_to_resource_item_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["resource_id"],
            ["competency_matrix_resources.id"],
            name="competency_matrix_item_to_resource_resource_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="competency_matrix_item_to_resource_pkey"),
    )
