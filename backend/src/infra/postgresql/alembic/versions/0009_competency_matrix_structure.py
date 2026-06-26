import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None

ITEM_TABLE = "competency_matrix__competency_matrix_item_model"
SHEET_TABLE = "competency_matrix__competency_matrix_sheet_model"
SECTION_TABLE = "competency_matrix__competency_matrix_section_model"
SUBSECTION_TABLE = "competency_matrix__competency_matrix_subsection_model"

ID_TYPE = sa.BigInteger().with_variant(sa.Integer(), "sqlite")
MISSING_FIELDS_EXPRESSION = (
    "((length(trim(slug)) = 0) OR "
    "(grade IS NULL) OR "
    "(length(trim(question_ru)) = 0) OR "
    "(length(trim(question_en)) = 0) OR "
    "(length(trim(answer_ru)) = 0) OR "
    "(length(trim(answer_en)) = 0) OR "
    "(length(trim(interview_expected_answer_ru)) = 0) OR "
    "(length(trim(interview_expected_answer_en)) = 0))"
)
OLD_MISSING_FIELDS_EXPRESSION = (
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


metadata = sa.MetaData()
item_table = sa.Table(
    ITEM_TABLE,
    metadata,
    sa.Column("id", ID_TYPE),
    sa.Column("sheet_key", sa.String(length=255)),
    sa.Column("sheet_ru", sa.String(length=255)),
    sa.Column("sheet_en", sa.String(length=255)),
    sa.Column("section_ru", sa.String(length=255)),
    sa.Column("section_en", sa.String(length=255)),
    sa.Column("subsection_ru", sa.String(length=255)),
    sa.Column("subsection_en", sa.String(length=255)),
    sa.Column("subsection_id", ID_TYPE),
)
sheet_table = sa.Table(
    SHEET_TABLE,
    metadata,
    sa.Column("id", ID_TYPE),
    sa.Column("key", sa.String(length=255)),
    sa.Column("name_ru", sa.String(length=255)),
    sa.Column("name_en", sa.String(length=255)),
)
section_table = sa.Table(
    SECTION_TABLE,
    metadata,
    sa.Column("id", ID_TYPE),
    sa.Column("sheet_id", ID_TYPE),
    sa.Column("name_ru", sa.String(length=255)),
    sa.Column("name_en", sa.String(length=255)),
)
subsection_table = sa.Table(
    SUBSECTION_TABLE,
    metadata,
    sa.Column("id", ID_TYPE),
    sa.Column("section_id", ID_TYPE),
    sa.Column("name_ru", sa.String(length=255)),
    sa.Column("name_en", sa.String(length=255)),
)


def upgrade() -> None:
    create_structure_tables()
    validate_existing_structure_values()
    migrate_structure_values()
    add_item_subsection_reference()
    drop_old_item_structure_indexes()
    create_new_item_structure_indexes()
    drop_old_item_structure_columns()


def downgrade() -> None:
    add_old_item_structure_columns()
    restore_old_item_structure_values()
    drop_new_item_structure_indexes()
    drop_item_subsection_reference()
    recreate_old_item_structure_indexes()
    drop_structure_tables()


def create_structure_tables() -> None:
    op.create_table(
        SHEET_TABLE,
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("id", ID_TYPE, autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f(f"pk_{SHEET_TABLE}")),
        sa.UniqueConstraint("key", name=op.f(f"uq_{SHEET_TABLE}_key")),
    )
    op.create_index(
        "cm_sheet_key_lower_idx",
        SHEET_TABLE,
        [sa.func.lower(sa.column("key")).label("sheet_key_lower")],
        unique=False,
    )
    op.create_table(
        SECTION_TABLE,
        sa.Column("sheet_id", ID_TYPE, nullable=False),
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("id", ID_TYPE, autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["sheet_id"],
            [f"{SHEET_TABLE}.id"],
            name=op.f(f"fk_{SECTION_TABLE}_sheet_id_{SHEET_TABLE}"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f(f"pk_{SECTION_TABLE}")),
        sa.UniqueConstraint("sheet_id", "name_ru", name="cm_section_sheet_name_ru_uniq"),
        sa.UniqueConstraint("sheet_id", "name_en", name="cm_section_sheet_name_en_uniq"),
    )
    op.create_index("cm_section_sheet_en_idx", SECTION_TABLE, ["sheet_id", "name_en", "id"])
    op.create_index("cm_section_sheet_ru_idx", SECTION_TABLE, ["sheet_id", "name_ru", "id"])
    op.create_table(
        SUBSECTION_TABLE,
        sa.Column("section_id", ID_TYPE, nullable=False),
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("id", ID_TYPE, autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["section_id"],
            [f"{SECTION_TABLE}.id"],
            name=op.f(f"fk_{SUBSECTION_TABLE}_section_id_{SECTION_TABLE}"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f(f"pk_{SUBSECTION_TABLE}")),
        sa.UniqueConstraint(
            "section_id",
            "name_ru",
            name="cm_subsection_section_name_ru_uniq",
        ),
        sa.UniqueConstraint(
            "section_id",
            "name_en",
            name="cm_subsection_section_name_en_uniq",
        ),
    )
    op.create_index(
        "cm_subsection_section_en_idx",
        SUBSECTION_TABLE,
        ["section_id", "name_en", "id"],
    )
    op.create_index(
        "cm_subsection_section_ru_idx",
        SUBSECTION_TABLE,
        ["section_id", "name_ru", "id"],
    )


def validate_existing_structure_values() -> None:
    connection = op.get_bind()
    blank_count = connection.scalar(
        sa.select(sa.func.count())
        .select_from(item_table)
        .where(
            sa.or_(
                blank(item_table.c.sheet_key),
                blank(item_table.c.sheet_ru),
                blank(item_table.c.sheet_en),
                blank(item_table.c.section_ru),
                blank(item_table.c.section_en),
                blank(item_table.c.subsection_ru),
                blank(item_table.c.subsection_en),
            ),
        ),
    )
    if blank_count:
        msg = "Cannot migrate competency matrix structure with blank taxonomy fields."
        raise ValueError(msg)


def migrate_structure_values() -> None:
    op.execute(
        sa.insert(sheet_table).from_select(
            ["key", "name_ru", "name_en"],
            sa.select(
                item_table.c.sheet_key,
                item_table.c.sheet_ru,
                item_table.c.sheet_en,
            ).distinct(),
        ),
    )
    op.execute(
        sa.insert(section_table).from_select(
            ["sheet_id", "name_ru", "name_en"],
            sa.select(
                sheet_table.c.id,
                item_table.c.section_ru,
                item_table.c.section_en,
            )
            .select_from(item_table.join(sheet_table, sheet_table.c.key == item_table.c.sheet_key))
            .distinct(),
        ),
    )
    op.execute(
        sa.insert(subsection_table).from_select(
            ["section_id", "name_ru", "name_en"],
            sa.select(
                section_table.c.id,
                item_table.c.subsection_ru,
                item_table.c.subsection_en,
            )
            .select_from(
                item_table.join(sheet_table, sheet_table.c.key == item_table.c.sheet_key).join(
                    section_table,
                    sa.and_(
                        section_table.c.sheet_id == sheet_table.c.id,
                        section_table.c.name_ru == item_table.c.section_ru,
                        section_table.c.name_en == item_table.c.section_en,
                    ),
                ),
            )
            .distinct(),
        ),
    )


def add_item_subsection_reference() -> None:
    op.add_column(ITEM_TABLE, sa.Column("subsection_id", ID_TYPE, nullable=True))
    subsection_lookup = (
        sa.select(subsection_table.c.id)
        .select_from(
            subsection_table.join(
                section_table,
                section_table.c.id == subsection_table.c.section_id,
            ).join(sheet_table, sheet_table.c.id == section_table.c.sheet_id),
        )
        .where(
            sheet_table.c.key == item_table.c.sheet_key,
            section_table.c.name_ru == item_table.c.section_ru,
            section_table.c.name_en == item_table.c.section_en,
            subsection_table.c.name_ru == item_table.c.subsection_ru,
            subsection_table.c.name_en == item_table.c.subsection_en,
        )
        .scalar_subquery()
    )
    op.execute(item_table.update().values(subsection_id=subsection_lookup))
    connection = op.get_bind()
    missing_reference_count = connection.scalar(
        sa.select(sa.func.count())
        .select_from(item_table)
        .where(item_table.c.subsection_id.is_(None)),
    )
    if missing_reference_count:
        msg = "Cannot migrate competency matrix items without a subsection reference."
        raise ValueError(msg)
    op.alter_column(ITEM_TABLE, "subsection_id", existing_type=ID_TYPE, nullable=False)
    op.create_foreign_key(
        "cmi_subsection_fk",
        ITEM_TABLE,
        SUBSECTION_TABLE,
        ["subsection_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def drop_old_item_structure_indexes() -> None:
    for index_name in (
        "cmi_sheet_key_status_order_idx",
        "cmi_workspace_sheet_status_grade_idx",
        "cmi_workspace_ru_structure_idx",
        "cmi_workspace_en_structure_idx",
        "cmi_workspace_missing_fields_idx",
    ):
        op.drop_index(index_name, table_name=ITEM_TABLE)


def create_new_item_structure_indexes() -> None:
    op.create_index(
        "cmi_subsection_status_grade_idx",
        ITEM_TABLE,
        ["subsection_id", "publish_status", "grade", "id"],
    )
    op.create_index(
        "cmi_workspace_subsection_status_grade_idx",
        ITEM_TABLE,
        ["subsection_id", "publish_status", "grade", "id"],
    )
    op.create_index(
        "cmi_workspace_missing_fields_idx",
        ITEM_TABLE,
        [sa.text(MISSING_FIELDS_EXPRESSION)],
    )


def drop_old_item_structure_columns() -> None:
    for column_name in (
        "sheet_key",
        "sheet_ru",
        "sheet_en",
        "section_ru",
        "section_en",
        "subsection_ru",
        "subsection_en",
    ):
        op.drop_column(ITEM_TABLE, column_name)


def add_old_item_structure_columns() -> None:
    for column_name in (
        "sheet_key",
        "sheet_ru",
        "sheet_en",
        "section_ru",
        "section_en",
        "subsection_ru",
        "subsection_en",
    ):
        op.add_column(ITEM_TABLE, sa.Column(column_name, sa.String(length=255), nullable=True))


def restore_old_item_structure_values() -> None:
    op.execute(
        item_table.update().values(
            sheet_key=sheet_table.c.key,
            sheet_ru=sheet_table.c.name_ru,
            sheet_en=sheet_table.c.name_en,
            section_ru=section_table.c.name_ru,
            section_en=section_table.c.name_en,
            subsection_ru=subsection_table.c.name_ru,
            subsection_en=subsection_table.c.name_en,
        )
        .where(item_table.c.subsection_id == subsection_table.c.id)
        .where(subsection_table.c.section_id == section_table.c.id)
        .where(section_table.c.sheet_id == sheet_table.c.id),
    )
    for column_name in (
        "sheet_key",
        "sheet_ru",
        "sheet_en",
        "section_ru",
        "section_en",
        "subsection_ru",
        "subsection_en",
    ):
        op.alter_column(ITEM_TABLE, column_name, existing_type=sa.String(length=255), nullable=False)


def drop_new_item_structure_indexes() -> None:
    for index_name in (
        "cmi_workspace_missing_fields_idx",
        "cmi_workspace_subsection_status_grade_idx",
        "cmi_subsection_status_grade_idx",
    ):
        op.drop_index(index_name, table_name=ITEM_TABLE)


def drop_item_subsection_reference() -> None:
    op.drop_constraint("cmi_subsection_fk", ITEM_TABLE, type_="foreignkey")
    op.drop_column(ITEM_TABLE, "subsection_id")


def recreate_old_item_structure_indexes() -> None:
    op.create_index(
        "cmi_sheet_key_status_order_idx",
        ITEM_TABLE,
        [
            sa.func.lower(sa.column("sheet_key")).label("sheet_key_lower"),
            "publish_status",
            "section_en",
            "subsection_en",
            "grade",
            "id",
        ],
    )
    op.create_index(
        "cmi_workspace_sheet_status_grade_idx",
        ITEM_TABLE,
        ["sheet_key", "publish_status", "grade", "id"],
        postgresql_include=("sheet_key", "sheet_ru", "sheet_en"),
    )
    op.create_index(
        "cmi_workspace_ru_structure_idx",
        ITEM_TABLE,
        ["section_ru", "subsection_ru", "grade", "id"],
        postgresql_include=("sheet_key", "publish_status"),
    )
    op.create_index(
        "cmi_workspace_en_structure_idx",
        ITEM_TABLE,
        ["section_en", "subsection_en", "grade", "id"],
        postgresql_include=("sheet_key", "publish_status"),
    )
    op.create_index(
        "cmi_workspace_missing_fields_idx",
        ITEM_TABLE,
        [sa.text(OLD_MISSING_FIELDS_EXPRESSION)],
    )


def drop_structure_tables() -> None:
    op.drop_index("cm_subsection_section_ru_idx", table_name=SUBSECTION_TABLE)
    op.drop_index("cm_subsection_section_en_idx", table_name=SUBSECTION_TABLE)
    op.drop_table(SUBSECTION_TABLE)
    op.drop_index("cm_section_sheet_ru_idx", table_name=SECTION_TABLE)
    op.drop_index("cm_section_sheet_en_idx", table_name=SECTION_TABLE)
    op.drop_table(SECTION_TABLE)
    op.drop_index("cm_sheet_key_lower_idx", table_name=SHEET_TABLE)
    op.drop_table(SHEET_TABLE)


def blank(column: sa.Column[str]) -> sa.ColumnElement[bool]:
    return sa.func.length(sa.func.trim(column)) == 0
