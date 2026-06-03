from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import Select

from performance.query_plans import (
    PlanExpectation,
    analyze_explain_result,
    capture_balanced_queries,
    compile_captured_query,
    generate_series_subquery,
)


def test_query_plan_package_is_split_into_focused_modules() -> None:
    module_names = {
        "analysis",
        "capture",
        "cli",
        "models",
        "reports",
        "runner",
        "seed",
        "sql",
    }

    for module_name in module_names:
        __import__(f"performance.query_plans.{module_name}")


class TestQueryPlanAnalysis:
    def test_analyze_explain_result_accepts_expected_index_scan(self) -> None:
        analysis = analyze_explain_result(
            name="notes_list_en",
            explain_json=[
                {
                    "Planning Time": 1.5,
                    "Execution Time": 42.0,
                    "Plan": {
                        "Node Type": "Limit",
                        "Actual Rows": 20,
                        "Plans": [
                            {
                                "Node Type": "Bitmap Heap Scan",
                                "Relation Name": "notes__note_model",
                                "Actual Rows": 120,
                                "Plans": [
                                    {
                                        "Node Type": "Bitmap Index Scan",
                                        "Index Name": "notes_note_search_vector_en_gin_idx",
                                        "Actual Rows": 120,
                                    },
                                ],
                            },
                        ],
                    },
                },
            ],
            expectation=PlanExpectation(
                max_execution_ms=150.0,
                expected_index_names=("notes_note_search_vector_en_gin_idx",),
                forbidden_seq_scan_relations=("notes__note_model",),
                allow_seq_scan_reason=None,
            ),
        )

        assert analysis.execution_time_ms == 42.0
        assert analysis.index_names == ("notes_note_search_vector_en_gin_idx",)
        assert analysis.findings == ()

    def test_analyze_explain_result_flags_missing_index_and_large_seq_scan(self) -> None:
        analysis = analyze_explain_result(
            name="notes_list_en",
            explain_json=[
                {
                    "Planning Time": 2.0,
                    "Execution Time": 312.0,
                    "Plan": {
                        "Node Type": "Seq Scan",
                        "Relation Name": "notes__note_model",
                        "Actual Rows": 200_000,
                    },
                },
            ],
            expectation=PlanExpectation(
                max_execution_ms=150.0,
                expected_index_names=("notes_note_search_vector_en_gin_idx",),
                forbidden_seq_scan_relations=("notes__note_model",),
                allow_seq_scan_reason=None,
            ),
        )

        assert "notes_note_search_vector_en_gin_idx" in analysis.findings[0]
        assert "Seq Scan on notes__note_model" in analysis.findings[1]
        assert "312.00 ms exceeded 150.00 ms" in analysis.findings[2]


class TestQueryCapture:
    def test_generate_series_subquery_exposes_value_column(self) -> None:
        series = generate_series_subquery(end=3, name="sample_series")

        compiled = str(
            series.select().compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            ),
        )

        assert "generate_series(1, 3) AS value" in compiled
        assert "sample_series.value" in compiled

    async def test_capture_balanced_queries_uses_real_storage_selects(self) -> None:
        queries = await capture_balanced_queries()

        query_by_name = {query.name: query for query in queries}

        assert isinstance(query_by_name["notes_list_en_full_text_tag_date"].statement, Select)
        assert isinstance(query_by_name["notes_count_en_full_text_tag_date"].statement, Select)
        assert isinstance(query_by_name["matrix_public_detail_by_slug"].statement, Select)
        assert isinstance(query_by_name["tags_fuzzy_en"].statement, Select)
        assert isinstance(query_by_name["resources_fuzzy_en"].statement, Select)

    async def test_compile_captured_query_keeps_sql_and_params_separate(self) -> None:
        queries = await capture_balanced_queries()
        query = next(item for item in queries if item.name == "tags_fuzzy_en")

        compiled = compile_captured_query(query=query, dialect=postgresql.dialect())

        assert "FROM notes__tag_model" in compiled.sql
        assert "tag_search_query" in compiled.params
        assert compiled.params["tag_search_query"] == "pythno"
