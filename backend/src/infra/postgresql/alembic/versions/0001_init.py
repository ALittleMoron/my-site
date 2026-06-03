import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_table(
        "auth__user_model",
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=127), nullable=False),
        sa.Column(
            "role",
            sa.Enum("ANON", "USER", "ADMIN", name="role_enum", native_enum=False, length=10),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("username"),
    )
    op.create_index("users_username_idx", "auth__user_model", ["username"], unique=False)
    op.create_table(
        "notes__note_model",
        sa.Column("title_ru", sa.String(length=255), nullable=False),
        sa.Column("title_en", sa.String(length=255), nullable=False),
        sa.Column("content_ru", sa.String(), nullable=False),
        sa.Column("content_en", sa.String(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("folder_ru", sa.String(length=255), nullable=False),
        sa.Column("folder_en", sa.String(length=255), nullable=False),
        sa.Column("author_username", sa.String(length=255), nullable=False),
        sa.Column("seo_title_ru", sa.String(length=255), nullable=True),
        sa.Column("seo_title_en", sa.String(length=255), nullable=True),
        sa.Column("seo_description_ru", sa.String(length=320), nullable=True),
        sa.Column("seo_description_en", sa.String(length=320), nullable=True),
        sa.Column("cover_image_url", sa.String(length=2048), nullable=True),
        sa.Column("cover_image_alt_ru", sa.String(length=255), nullable=True),
        sa.Column("cover_image_alt_en", sa.String(length=255), nullable=True),
        sa.Column(
            "search_vector_ru",
            postgresql.TSVECTOR(),
            sa.Computed(
                "setweight(to_tsvector('simple', coalesce(title_ru, '')), 'A') || "
                "setweight(to_tsvector('simple', coalesce(content_ru, '')), 'B')",
                persisted=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "search_vector_en",
            postgresql.TSVECTOR(),
            sa.Computed(
                "setweight(to_tsvector('simple', coalesce(title_en, '')), 'A') || "
                "setweight(to_tsvector('simple', coalesce(content_en, '')), 'B')",
                persisted=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "published_at",
            UTCDateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "publish_status",
            sa.Enum("DRAFT", "PUBLISHED", name="publish_status_enum", native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notes__note_model_slug"),
        "notes__note_model",
        ["slug"],
        unique=True,
    )
    op.create_index(
        "notes_note_search_vector_gin_idx",
        "notes__note_model",
        ["search_vector_ru"],
        unique=False,
        postgresql_using="gin",
    )
    op.create_index(
        "notes_note_search_vector_en_gin_idx",
        "notes__note_model",
        ["search_vector_en"],
        unique=False,
        postgresql_using="gin",
    )
    op.create_index(
        "notes_note_publish_status_published_at_idx",
        "notes__note_model",
        ["publish_status", "published_at"],
        unique=False,
    )
    op.create_index(
        "notes_note_publish_status_published_updated_idx",
        "notes__note_model",
        [
            "publish_status",
            sa.text("published_at DESC NULLS LAST"),
            sa.text("updated_at DESC"),
        ],
        unique=False,
    )
    op.create_table(
        "notes__tag_model",
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("deleted_at", UTCDateTime(timezone=True), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notes__tag_model_slug"), "notes__tag_model", ["slug"], unique=True)
    op.create_index(
        "notes_tag_name_ru_trgm_idx",
        "notes__tag_model",
        [sa.func.lower(sa.column("name_ru")).label("name_ru_lower")],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name_ru_lower": "gin_trgm_ops"},
    )
    op.create_index(
        "notes_tag_name_en_trgm_idx",
        "notes__tag_model",
        [sa.func.lower(sa.column("name_en")).label("name_en_lower")],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name_en_lower": "gin_trgm_ops"},
    )
    op.create_index(
        "notes_tag_slug_trgm_idx",
        "notes__tag_model",
        [sa.func.lower(sa.column("slug")).label("slug_lower")],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"slug_lower": "gin_trgm_ops"},
    )
    op.create_table(
        "competency_matrix__competency_matrix_item_model",
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("question_ru", sa.String(length=255), nullable=False),
        sa.Column("question_en", sa.String(length=255), nullable=False),
        sa.Column("answer_ru", sa.String(), nullable=False),
        sa.Column("answer_en", sa.String(), nullable=False),
        sa.Column("interview_expected_answer_ru", sa.String(), nullable=False),
        sa.Column("interview_expected_answer_en", sa.String(), nullable=False),
        sa.Column("sheet_key", sa.String(length=255), nullable=False),
        sa.Column("sheet_ru", sa.String(length=255), nullable=False),
        sa.Column("sheet_en", sa.String(length=255), nullable=False),
        sa.Column("section_ru", sa.String(length=255), nullable=False),
        sa.Column("section_en", sa.String(length=255), nullable=False),
        sa.Column("subsection_ru", sa.String(length=255), nullable=False),
        sa.Column("subsection_en", sa.String(length=255), nullable=False),
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
            ),
            nullable=False,
        ),
        sa.Column(
            "published_at",
            UTCDateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "publish_status",
            sa.Enum("DRAFT", "PUBLISHED", name="publish_status_enum", native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "cmi_sheet_key_idx",
        "competency_matrix__competency_matrix_item_model",
        [sa.func.lower(sa.column("sheet_key")).label("sheet_key_lower")],
        unique=False,
    )
    op.create_index(
        op.f("ix_competency_matrix__competency_matrix_item_model_slug"),
        "competency_matrix__competency_matrix_item_model",
        ["slug"],
        unique=True,
    )
    op.create_table(
        "competency_matrix__external_resource_model",
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "cm_external_resource_name_ru_trgm_idx",
        "competency_matrix__external_resource_model",
        [sa.func.lower(sa.column("name_ru")).label("name_ru_lower")],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name_ru_lower": "gin_trgm_ops"},
    )
    op.create_index(
        "cm_external_resource_name_en_trgm_idx",
        "competency_matrix__external_resource_model",
        [sa.func.lower(sa.column("name_en")).label("name_en_lower")],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name_en_lower": "gin_trgm_ops"},
    )
    op.create_index(
        "cm_external_resource_url_trgm_idx",
        "competency_matrix__external_resource_model",
        [sa.func.lower(sa.column("url")).label("url_lower")],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"url_lower": "gin_trgm_ops"},
    )
    op.create_table(
        "contacts__contact_me_model",
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("telegram", sa.String(length=256), nullable=True),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "competency_matrix__resource_to_item_secondary_model",
        sa.Column(
            "item_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "resource_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False,
        ),
        sa.Column("context_ru", sa.String(), nullable=False),
        sa.Column("context_en", sa.String(), nullable=False),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["item_id"], ["competency_matrix__competency_matrix_item_model.id"], ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["resource_id"], ["competency_matrix__external_resource_model.id"], ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id", "resource_id", name="cm_resource_item_uniq"),
    )
    op.create_table(
        "notes__note_to_tag_secondary_model",
        sa.Column("note_id", sa.UUID(), nullable=False),
        sa.Column(
            "tag_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["note_id"], ["notes__note_model.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["notes__tag_model.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("note_id", "tag_id", name="notes_note_tag_uniq"),
    )
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
    op.drop_table("notes__note_to_tag_secondary_model")
    op.drop_table("competency_matrix__resource_to_item_secondary_model")
    op.drop_table("contacts__contact_me_model")
    op.drop_index(
        "cm_external_resource_url_trgm_idx",
        table_name="competency_matrix__external_resource_model",
    )
    op.drop_index(
        "cm_external_resource_name_en_trgm_idx",
        table_name="competency_matrix__external_resource_model",
    )
    op.drop_index(
        "cm_external_resource_name_ru_trgm_idx",
        table_name="competency_matrix__external_resource_model",
    )
    op.drop_table("competency_matrix__external_resource_model")
    op.drop_index(
        "cmi_sheet_key_idx",
        table_name="competency_matrix__competency_matrix_item_model",
    )
    op.drop_index(
        op.f("ix_competency_matrix__competency_matrix_item_model_slug"),
        table_name="competency_matrix__competency_matrix_item_model",
    )
    op.drop_table("competency_matrix__competency_matrix_item_model")
    op.drop_index("notes_tag_slug_trgm_idx", table_name="notes__tag_model")
    op.drop_index("notes_tag_name_en_trgm_idx", table_name="notes__tag_model")
    op.drop_index("notes_tag_name_ru_trgm_idx", table_name="notes__tag_model")
    op.drop_index(op.f("ix_notes__tag_model_slug"), table_name="notes__tag_model")
    op.drop_table("notes__tag_model")
    op.drop_index(
        "notes_note_publish_status_published_updated_idx",
        table_name="notes__note_model",
    )
    op.drop_index(
        "notes_note_publish_status_published_at_idx",
        table_name="notes__note_model",
    )
    op.drop_index(
        "notes_note_search_vector_en_gin_idx",
        table_name="notes__note_model",
        postgresql_using="gin",
    )
    op.drop_index(
        "notes_note_search_vector_gin_idx",
        table_name="notes__note_model",
        postgresql_using="gin",
    )
    op.drop_index(op.f("ix_notes__note_model_slug"), table_name="notes__note_model")
    op.drop_table("notes__note_model")
    op.drop_index("users_username_idx", table_name="auth__user_model")
    op.drop_table("auth__user_model")
