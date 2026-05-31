from collections.abc import Sequence
from statistics import median
from sys import stderr, stdout
from typing import cast

from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine
from sqlalchemy.pool import NullPool

from infra.config.settings import settings
from infra.postgresql.utils import migrate
from performance.query_plans.analysis import analyze_explain_result, evaluate_plan_analysis
from performance.query_plans.capture import capture_balanced_queries
from performance.query_plans.models import (
    BALANCED_PROFILE,
    BenchmarkResult,
    CapturedQuery,
    CliArgs,
    DatasetProfile,
    PlanAnalysis,
)
from performance.query_plans.reports import write_reports
from performance.query_plans.seed import seed_profile, vacuum_analyze_seeded_tables
from performance.query_plans.sql import compile_captured_query, run_explain


async def run_query_plan_profile(args: CliArgs) -> int:
    profile = get_profile(name=args.profile)
    ensure_safe_database_name(allow_non_test_db=args.allow_non_test_db)
    migrate(revision="heads")
    engine = create_async_engine(settings.database.url.get_secret_value(), poolclass=NullPool)
    try:
        async with engine.begin() as connection:
            await seed_profile(connection=connection, profile=profile)
        async with engine.connect() as connection:
            autocommit_connection = await connection.execution_options(
                isolation_level="AUTOCOMMIT",
            )
            await vacuum_analyze_seeded_tables(connection=autocommit_connection)
        queries = await capture_balanced_queries()
        async with engine.connect() as connection:
            results = await benchmark_queries(
                connection=connection,
                queries=queries,
                profile=profile,
            )
        write_reports(report_dir=args.report_dir, profile=profile, results=results)
    finally:
        await engine.dispose()

    findings = tuple(finding for result in results for finding in result.findings)
    stdout.write(f"Query plan report written to {args.report_dir}\n")
    if findings:
        stderr.write("\n".join(f"- {finding}" for finding in findings))
        stderr.write("\n")
        return 1 if args.fail_on_finding else 0
    return 0


def get_profile(*, name: str) -> DatasetProfile:
    if name == BALANCED_PROFILE.name:
        return BALANCED_PROFILE
    msg = f"Unknown query plan profile: {name}"
    raise ValueError(msg)


def ensure_safe_database_name(*, allow_non_test_db: bool) -> None:
    database_name = settings.database.name
    if allow_non_test_db:
        return
    if database_name.endswith("_test"):
        return
    msg = (
        "query plan seeding clears tables and must run against a test database; "
        f"got DB_NAME={database_name!r}"
    )
    raise RuntimeError(msg)


async def benchmark_queries(
    *,
    connection: AsyncConnection,
    queries: Sequence[CapturedQuery],
    profile: DatasetProfile,
) -> tuple[BenchmarkResult, ...]:
    results: list[BenchmarkResult] = []
    for query in queries:
        stdout.write(f"Running EXPLAIN ANALYZE for {query.name}\n")
        compiled_query = compile_captured_query(query=query, dialect=connection.dialect)
        explain_json_runs: list[object] = []
        analyses: list[PlanAnalysis] = []
        for _ in range(profile.explain_runs):
            explain_json = await run_explain(connection=connection, compiled_query=compiled_query)
            explain_json_runs.append(explain_json)
            analyses.append(
                analyze_explain_result(
                    name=query.name,
                    explain_json=cast("Sequence[object]", explain_json),
                    expectation=query.expectation,
                ),
            )
        warm_execution_ms = median(analysis.execution_time_ms for analysis in analyses[1:])
        shape_findings = evaluate_plan_analysis(
            analysis=analyses[-1],
            expectation=query.expectation,
            measured_execution_ms=warm_execution_ms,
        )
        results.append(
            BenchmarkResult(
                query=query,
                compiled_query=compiled_query,
                explain_json_runs=tuple(explain_json_runs),
                analyses=tuple(analyses),
                warm_execution_ms=warm_execution_ms,
                findings=tuple(f"{query.name}: {finding}" for finding in shape_findings),
            ),
        )
    return tuple(results)
