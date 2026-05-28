from typing import cast

from sqlalchemy import Table
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex

from infra.postgresql.models.competency_matrix import ExternalResourceModel


def test_external_resource_model_defines_trigram_search_indexes() -> None:
    table = cast("Table", ExternalResourceModel.__table__)
    statements = {
        str(CreateIndex(index).compile(dialect=postgresql.dialect())) for index in table.indexes
    }

    assert {
        "CREATE INDEX cm_external_resource_name_trgm_idx "
        "ON competency_matrix__external_resource_model "
        "USING gin (lower(name) gin_trgm_ops)",
        "CREATE INDEX cm_external_resource_url_trgm_idx "
        "ON competency_matrix__external_resource_model "
        "USING gin (lower(url) gin_trgm_ops)",
    } <= statements
