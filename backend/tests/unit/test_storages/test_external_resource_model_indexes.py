from typing import cast

from sqlalchemy import Table
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex

from infra.postgresql.models.competency_matrix import (
    CompetencyMatrixItemModel,
    ExternalResourceModel,
)
from infra.postgresql.models.notes import NoteModel


def test_external_resource_model_defines_trigram_search_indexes() -> None:
    table = cast("Table", ExternalResourceModel.__table__)
    statements = {
        str(CreateIndex(index).compile(dialect=postgresql.dialect())) for index in table.indexes
    }

    assert {
        "CREATE INDEX cm_external_resource_name_ru_trgm_idx "
        "ON competency_matrix__external_resource_model "
        "USING gin (lower(name_ru) gin_trgm_ops)",
        "CREATE INDEX cm_external_resource_name_en_trgm_idx "
        "ON competency_matrix__external_resource_model "
        "USING gin (lower(name_en) gin_trgm_ops)",
        "CREATE INDEX cm_external_resource_url_trgm_idx "
        "ON competency_matrix__external_resource_model "
        "USING gin (lower(url) gin_trgm_ops)",
    } <= statements


def test_competency_matrix_item_model_defines_sheet_key_index() -> None:
    table = cast("Table", CompetencyMatrixItemModel.__table__)
    statements = {
        str(CreateIndex(index).compile(dialect=postgresql.dialect())) for index in table.indexes
    }

    assert {
        "CREATE INDEX cmi_sheet_key_idx "
        "ON competency_matrix__competency_matrix_item_model "
        "(lower(sheet_key))",
    } <= statements


def test_note_model_defines_search_and_publish_filter_indexes() -> None:
    table = cast("Table", NoteModel.__table__)
    search_vector_ru = table.c.search_vector_ru
    search_vector_en = table.c.search_vector_en
    statements = {
        str(CreateIndex(index).compile(dialect=postgresql.dialect())) for index in table.indexes
    }

    assert search_vector_ru.computed is not None
    assert search_vector_en.computed is not None
    assert "title_ru" in str(search_vector_ru.computed.sqltext)
    assert "content_en" in str(search_vector_en.computed.sqltext)
    assert {
        "CREATE INDEX notes_note_search_vector_gin_idx "
        "ON notes__note_model "
        "USING gin (search_vector_ru)",
        "CREATE INDEX notes_note_search_vector_en_gin_idx "
        "ON notes__note_model "
        "USING gin (search_vector_en)",
        "CREATE INDEX notes_note_publish_status_published_at_idx "
        "ON notes__note_model "
        "(publish_status, published_at)",
    } <= statements
