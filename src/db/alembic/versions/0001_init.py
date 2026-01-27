import sqlalchemy as sa
from alembic import op
from sqlalchemy_dev_utils.types.datetime import UTCDateTime

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
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
        "blog__blog_post_model",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
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
        op.f("ix_blog__blog_post_model_slug"), "blog__blog_post_model", ["slug"], unique=True,
    )
    op.create_table(
        "competency_matrix__competency_matrix_item_model",
        sa.Column("question", sa.String(length=255), nullable=False),
        sa.Column("answer", sa.String(), nullable=False),
        sa.Column("interview_expected_answer", sa.String(), nullable=False),
        sa.Column("sheet", sa.String(length=255), nullable=False),
        sa.Column("section", sa.String(length=255), nullable=False),
        sa.Column("subsection", sa.String(length=255), nullable=False),
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
        "cmi_sheet_idx",
        "competency_matrix__competency_matrix_item_model",
        [sa.literal_column("lower('sheet')")],
        unique=False,
    )
    op.create_table(
        "competency_matrix__external_resource_model",
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
        sa.Column("item_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False,),
        sa.Column(
            "resource_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False,
        ),
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
    )


def downgrade() -> None:
    op.drop_table("competency_matrix__resource_to_item_secondary_model")
    op.drop_table("contacts__contact_me_model")
    op.drop_table("competency_matrix__external_resource_model")
    op.drop_index("cmi_sheet_idx", table_name="competency_matrix__competency_matrix_item_model")
    op.drop_table("competency_matrix__competency_matrix_item_model")
    op.drop_index(op.f("ix_blog__blog_post_model_slug"), table_name="blog__blog_post_model")
    op.drop_table("blog__blog_post_model")
    op.drop_index("users_username_idx", table_name="auth__user_model")
    op.drop_table("auth__user_model")
