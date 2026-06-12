import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

COMPETENCY_MATRIX_ITEM_TABLE = "competency_matrix__competency_matrix_item_model"
GRADE_ENUM = sa.Enum(
    "JUNIOR",
    "JUNIOR_PLUS",
    "MIDDLE",
    "MIDDLE_PLUS",
    "SENIOR",
    name="grade_enum",
    native_enum=False,
    length=11,
)


def upgrade() -> None:
    op.alter_column(
        COMPETENCY_MATRIX_ITEM_TABLE,
        "grade",
        existing_type=GRADE_ENUM,
        nullable=True,
    )


def downgrade() -> None:
    competency_matrix_item = sa.table(
        COMPETENCY_MATRIX_ITEM_TABLE,
        sa.column("grade", GRADE_ENUM),
    )
    op.execute(
        sa.update(competency_matrix_item)
        .where(competency_matrix_item.c.grade.is_(None))
        .values(grade="JUNIOR"),
    )
    op.alter_column(
        COMPETENCY_MATRIX_ITEM_TABLE,
        "grade",
        existing_type=GRADE_ENUM,
        nullable=False,
    )
