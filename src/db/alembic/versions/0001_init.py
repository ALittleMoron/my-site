import sqlalchemy as sa
from alembic import op
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "competency_matrix_items",
        sa.Column("question", sa.String(length=255), nullable=False),
        sa.Column("answer", sa.String(), nullable=False),
        sa.Column("interview_expected_answer", sa.String(), nullable=False),
        sa.Column("sheet", sa.String(length=255), nullable=False),
        sa.Column("section", sa.String(length=255), nullable=False),
        sa.Column("subsection", sa.String(length=255), nullable=False),
        sa.Column("grade", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "PUBLISHED", name="statusenum", native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column(
            "status_changed",
            UTCDateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(
        "cmi_sheet_idx",
        "competency_matrix_items",
        [sa.literal_column("lower('sheet')")],
        unique=False,
    )
    op.create_table(
        "competency_matrix_resources",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("context", sa.String(), nullable=False),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "competency_matrix_item_to_resource",
        sa.Column(
            "resource_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("item_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
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
        sa.UniqueConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("competency_matrix_item_to_resource")
    op.drop_table("competency_matrix_resources")
    op.drop_index("cmi_sheet_idx", table_name="competency_matrix_items")
    op.drop_table("competency_matrix_items")
