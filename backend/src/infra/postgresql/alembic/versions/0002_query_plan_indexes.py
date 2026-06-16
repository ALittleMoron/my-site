import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "articles_article_tree_ru_published_idx",
        "articles__article_model",
        [
            "folder_ru",
            sa.text("published_at DESC NULLS LAST"),
            sa.text("updated_at DESC"),
            "title_ru",
        ],
        unique=False,
        postgresql_include=("slug", "publish_status"),
        postgresql_where=sa.text("publish_status = 'PUBLISHED'"),
    )
    op.create_index(
        "articles_article_tree_en_published_idx",
        "articles__article_model",
        [
            "folder_en",
            sa.text("published_at DESC NULLS LAST"),
            sa.text("updated_at DESC"),
            "title_en",
        ],
        unique=False,
        postgresql_include=("slug", "publish_status"),
        postgresql_where=sa.text("publish_status = 'PUBLISHED'"),
    )
    op.drop_index(
        "cmi_sheet_key_idx",
        table_name="competency_matrix__competency_matrix_item_model",
    )
    op.create_index(
        "cmi_sheet_key_status_order_idx",
        "competency_matrix__competency_matrix_item_model",
        [
            sa.func.lower(sa.column("sheet_key")).label("sheet_key_lower"),
            "publish_status",
            "section_en",
            "subsection_en",
            "grade",
            "id",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "cmi_sheet_key_status_order_idx",
        table_name="competency_matrix__competency_matrix_item_model",
    )
    op.create_index(
        "cmi_sheet_key_idx",
        "competency_matrix__competency_matrix_item_model",
        [sa.func.lower(sa.column("sheet_key")).label("sheet_key_lower")],
        unique=False,
    )
    op.drop_index(
        "articles_article_tree_en_published_idx",
        table_name="articles__article_model",
    )
    op.drop_index(
        "articles_article_tree_ru_published_idx",
        table_name="articles__article_model",
    )
