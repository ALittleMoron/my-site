import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "competency_matrix_items",
        "grade",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.Enum(
            "JUNIOR",
            "JUNIOR_PLUS",
            "MIDDLE",
            "MIDDLE_PLUS",
            "SENIOR",
            name="gradeenum",
            native_enum=False,
        ),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "competency_matrix_items",
        "grade",
        existing_type=sa.Enum(
            "JUNIOR",
            "JUNIOR_PLUS",
            "MIDDLE",
            "MIDDLE_PLUS",
            "SENIOR",
            name="gradeenum",
            native_enum=False,
        ),
        type_=sa.VARCHAR(length=255),
        existing_nullable=False,
    )
