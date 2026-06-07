import sqlalchemy as sa
from alembic import op
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "competency_matrix__queued_question_model",
        sa.Column("question", sa.String(length=255), nullable=False),
        sa.Column(
            "grade",
            sa.Enum(
                "JUNIOR",
                "JUNIOR_PLUS",
                "MIDDLE",
                "MIDDLE_PLUS",
                "SENIOR",
                name="grade_enum",
                native_enum=False,
                length=11,
            ),
            nullable=True,
        ),
        sa.Column("sheet", sa.String(length=255), nullable=True),
        sa.Column("section", sa.String(length=255), nullable=True),
        sa.Column("subsection", sa.String(length=255), nullable=True),
        sa.Column("suggested_by_username", sa.String(length=255), nullable=True),
        sa.Column("created_at", UTCDateTime(timezone=True), nullable=False),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["suggested_by_username"],
            ["auth__user_model.username"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "cm_queued_question_fifo_idx",
        "competency_matrix__queued_question_model",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "cm_queued_question_suggested_by_idx",
        "competency_matrix__queued_question_model",
        ["suggested_by_username"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "cm_queued_question_suggested_by_idx",
        table_name="competency_matrix__queued_question_model",
    )
    op.drop_index(
        "cm_queued_question_fifo_idx",
        table_name="competency_matrix__queued_question_model",
    )
    op.drop_table("competency_matrix__queued_question_model")
