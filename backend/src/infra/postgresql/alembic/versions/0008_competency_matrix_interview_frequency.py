import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None

COMPETENCY_MATRIX_ITEM_TABLE = "competency_matrix__competency_matrix_item_model"
INTERVIEW_FREQUENCY_ENUM = sa.Enum(
    "CONSTANTLY",
    "OFTEN",
    "RARELY",
    "NEVER_SEEN",
    name="interview_frequency_enum",
    native_enum=False,
    length=11,
)


def upgrade() -> None:
    op.add_column(
        COMPETENCY_MATRIX_ITEM_TABLE,
        sa.Column("interview_frequency", INTERVIEW_FREQUENCY_ENUM, nullable=True),
    )


def downgrade() -> None:
    op.drop_column(COMPETENCY_MATRIX_ITEM_TABLE, "interview_frequency")
