import json
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from enum import Enum
from pathlib import Path

from performance.query_plans.models import BenchmarkResult, CoverageReport, DatasetProfile


def write_reports(
    *,
    report_dir: Path,
    profile: DatasetProfile,
    coverage: CoverageReport,
    results: Sequence[BenchmarkResult],
) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    for result in results:
        result_path = report_dir / result.query.name
        result_path.mkdir(parents=True, exist_ok=True)
        (result_path / "compiled.sql").write_text(result.compiled_query.sql, encoding="utf-8")
        (result_path / "params.json").write_text(
            json.dumps(
                result.compiled_query.params,
                ensure_ascii=False,
                indent=2,
                default=json_default,
            ),
            encoding="utf-8",
        )
        for index, explain_json in enumerate(result.explain_json_runs, start=1):
            (result_path / f"explain-run-{index}.json").write_text(
                json.dumps(explain_json, ensure_ascii=False, indent=2, default=json_default),
                encoding="utf-8",
            )
    (report_dir / "summary.md").write_text(
        render_markdown_summary(profile=profile, coverage=coverage, results=results),
        encoding="utf-8",
    )
    (report_dir / "summary.json").write_text(
        json.dumps(
            serialize_summary(profile=profile, coverage=coverage, results=results),
            ensure_ascii=False,
            indent=2,
            default=json_default,
        ),
        encoding="utf-8",
    )


def render_markdown_summary(
    *,
    profile: DatasetProfile,
    coverage: CoverageReport,
    results: Sequence[BenchmarkResult],
) -> str:
    lines = [
        "# Query Plan Report",
        "",
        f"- Profile: `{profile.name}`",
        f"- Articles: `{profile.article_count}`",
        f"- Tags: `{profile.tag_count}`",
        f"- Article-tag links: `{profile.article_tag_link_count}`",
        f"- Resources: `{profile.resource_count}`",
        f"- EXPLAIN runs per query: `{profile.explain_runs}`",
        f"- Storage methods discovered: `{len(coverage.discovered_methods)}`",
        f"- Storage methods covered: `{len(coverage.covered_methods)}`",
        f"- Missing storage scenarios: `{len(coverage.missing_methods)}`",
        f"- Unexpected storage scenarios: `{len(coverage.unexpected_methods)}`",
        "",
        "| Query | Storage method | Runtime ms | Warm median ms | Threshold | Indexes | "
        "Seq scans | Findings |",
        "|---|---|---:|---:|---|---|---|---|",
    ]
    for result in results:
        last_analysis = result.analyses[-1]
        indexes = ", ".join(last_analysis.index_names) or "-"
        seq_scans = ", ".join(last_analysis.seq_scan_relations) or "-"
        findings = "<br>".join(result.findings) or "OK"
        lines.append(
            f"| `{result.query.name}` | "
            f"`{result.query.storage_class}.{result.query.method_name}` | "
            f"{result.query.elapsed_ms:.2f} | {result.warm_execution_ms:.2f} | "
            f"{result.query.expectation.max_execution_ms:.2f} "
            f"({result.query.expectation.threshold_source}) | "
            f"{indexes} | {seq_scans} | {findings} |",
        )
    lines.append("")
    lines.append(
        "Each query directory contains the compiled SQL, bound params, and every "
        "`EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)` run.",
    )
    lines.append("")
    return "\n".join(lines)


def serialize_summary(
    *,
    profile: DatasetProfile,
    coverage: CoverageReport,
    results: Sequence[BenchmarkResult],
) -> Mapping[str, object]:
    return {
        "profile": {
            "name": profile.name,
            "articleCount": profile.article_count,
            "tagCount": profile.tag_count,
            "articleTagLinkCount": profile.article_tag_link_count,
            "resourceCount": profile.resource_count,
            "explainRuns": profile.explain_runs,
        },
        "coverage": {
            "discoveredMethodCount": len(coverage.discovered_methods),
            "coveredMethodCount": len(coverage.covered_methods),
            "missingMethods": [
                f"{method.storage_class}.{method.method_name}"
                for method in coverage.missing_methods
            ],
            "unexpectedMethods": [
                f"{method.storage_class}.{method.method_name}"
                for method in coverage.unexpected_methods
            ],
        },
        "results": [
            {
                "name": result.query.name,
                "storageClass": result.query.storage_class,
                "methodName": result.query.method_name,
                "scenarioName": result.query.scenario_name,
                "ordinal": result.query.ordinal,
                "executemany": result.query.executemany,
                "runtimeElapsedMs": result.query.elapsed_ms,
                "warmExecutionMs": result.warm_execution_ms,
                "thresholdSource": result.query.expectation.threshold_source,
                "maxExecutionMs": result.query.expectation.max_execution_ms,
                "indexes": result.analyses[-1].index_names,
                "seqScans": result.analyses[-1].seq_scan_relations,
                "nodeTypes": result.analyses[-1].node_types,
                "findings": result.findings,
            }
            for result in results
        ],
    }


def json_default(value: object) -> str:
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.name
    return str(value)
