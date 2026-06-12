import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

COMPETENCY_MATRIX_ITEM_TABLE = "competency_matrix__competency_matrix_item_model"
MISSING_FIELDS_EXPRESSION = (
    "((length(trim(slug)) = 0) OR "
    "(length(trim(sheet_key)) = 0) OR "
    "(grade IS NULL) OR "
    "(length(trim(question_ru)) = 0) OR "
    "(length(trim(question_en)) = 0) OR "
    "(length(trim(answer_ru)) = 0) OR "
    "(length(trim(answer_en)) = 0) OR "
    "(length(trim(interview_expected_answer_ru)) = 0) OR "
    "(length(trim(interview_expected_answer_en)) = 0) OR "
    "(length(trim(sheet_ru)) = 0) OR "
    "(length(trim(sheet_en)) = 0) OR "
    "(length(trim(section_ru)) = 0) OR "
    "(length(trim(section_en)) = 0) OR "
    "(length(trim(subsection_ru)) = 0) OR "
    "(length(trim(subsection_en)) = 0))"
)


def upgrade() -> None:
    op.create_index(
        "cmi_workspace_status_published_at_idx",
        COMPETENCY_MATRIX_ITEM_TABLE,
        [
            "publish_status",
            sa.text("published_at DESC NULLS LAST"),
            "id",
        ],
        unique=False,
    )
    op.create_index(
        "cmi_workspace_sheet_status_grade_idx",
        COMPETENCY_MATRIX_ITEM_TABLE,
        [
            "sheet_key",
            "publish_status",
            "grade",
            "id",
        ],
        unique=False,
        postgresql_include=("sheet_key", "sheet_ru", "sheet_en"),
    )
    op.create_index(
        "cmi_workspace_ru_structure_idx",
        COMPETENCY_MATRIX_ITEM_TABLE,
        [
            "section_ru",
            "subsection_ru",
            "grade",
            "id",
        ],
        unique=False,
        postgresql_include=("sheet_key", "publish_status"),
    )
    op.create_index(
        "cmi_workspace_en_structure_idx",
        COMPETENCY_MATRIX_ITEM_TABLE,
        [
            "section_en",
            "subsection_en",
            "grade",
            "id",
        ],
        unique=False,
        postgresql_include=("sheet_key", "publish_status"),
    )
    op.create_index(
        "cmi_workspace_missing_fields_idx",
        COMPETENCY_MATRIX_ITEM_TABLE,
        [sa.text(MISSING_FIELDS_EXPRESSION)],
        unique=False,
    )
    op.create_index(
        "cmi_workspace_slug_trgm_idx",
        COMPETENCY_MATRIX_ITEM_TABLE,
        [sa.func.lower(sa.column("slug")).label("workspace_slug_lower")],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"workspace_slug_lower": "gin_trgm_ops"},
    )
    op.create_index(
        "cmi_workspace_question_ru_trgm_idx",
        COMPETENCY_MATRIX_ITEM_TABLE,
        [sa.func.lower(sa.column("question_ru")).label("workspace_question_ru_lower")],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"workspace_question_ru_lower": "gin_trgm_ops"},
    )
    op.create_index(
        "cmi_workspace_question_en_trgm_idx",
        COMPETENCY_MATRIX_ITEM_TABLE,
        [sa.func.lower(sa.column("question_en")).label("workspace_question_en_lower")],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"workspace_question_en_lower": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index(
        "cmi_workspace_question_en_trgm_idx",
        table_name=COMPETENCY_MATRIX_ITEM_TABLE,
    )
    op.drop_index(
        "cmi_workspace_question_ru_trgm_idx",
        table_name=COMPETENCY_MATRIX_ITEM_TABLE,
    )
    op.drop_index(
        "cmi_workspace_slug_trgm_idx",
        table_name=COMPETENCY_MATRIX_ITEM_TABLE,
    )
    op.drop_index(
        "cmi_workspace_missing_fields_idx",
        table_name=COMPETENCY_MATRIX_ITEM_TABLE,
    )
    op.drop_index(
        "cmi_workspace_en_structure_idx",
        table_name=COMPETENCY_MATRIX_ITEM_TABLE,
    )
    op.drop_index(
        "cmi_workspace_ru_structure_idx",
        table_name=COMPETENCY_MATRIX_ITEM_TABLE,
    )
    op.drop_index(
        "cmi_workspace_sheet_status_grade_idx",
        table_name=COMPETENCY_MATRIX_ITEM_TABLE,
    )
    op.drop_index(
        "cmi_workspace_status_published_at_idx",
        table_name=COMPETENCY_MATRIX_ITEM_TABLE,
    )
