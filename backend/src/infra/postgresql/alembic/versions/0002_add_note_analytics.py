import sqlalchemy as sa
from alembic import op
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notes__note_daily_analytics_model",
        sa.Column("note_id", sa.UUID(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "source_category",
            sa.Enum(
                "DIRECT",
                "INTERNAL",
                "SEARCH",
                "SOCIAL",
                "EXTERNAL",
                "UNKNOWN",
                name="note_view_source_category_enum",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("view_count", sa.Integer(), nullable=False),
        sa.Column("engaged_view_count", sa.Integer(), nullable=False),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["note_id"], ["notes__note_model.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "note_id",
            "date",
            "source_category",
            name="notes_daily_analytics_note_date_source_uniq",
        ),
    )
    op.create_table(
        "notes__note_reaction_model",
        sa.Column("note_id", sa.UUID(), nullable=False),
        sa.Column("note_scoped_voter_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "reaction_kind",
            sa.Enum(
                "HEART",
                "FIRE",
                "THINKING",
                "NEUTRAL",
                "POOP",
                name="note_reaction_kind_enum",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            UTCDateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            UTCDateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["note_id"], ["notes__note_model.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "note_id",
            "note_scoped_voter_hash",
            name="notes_reaction_note_voter_uniq",
        ),
    )


def downgrade() -> None:
    op.drop_table("notes__note_reaction_model")
    op.drop_table("notes__note_daily_analytics_model")
