from collections.abc import Sequence
from dataclasses import replace
from statistics import median
from sys import stderr, stdout
from time import perf_counter_ns
from typing import cast

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from infra.config.settings import settings
from infra.postgresql.utils import migrate
from performance.query_plans.analysis import analyze_explain_result, evaluate_plan_analysis
from performance.query_plans.discovery import discover_storage_methods
from performance.query_plans.expectations import BALANCED_THRESHOLD_POLICY
from performance.query_plans.models import (
    BALANCED_PROFILE,
    BenchmarkResult,
    CapturedQuery,
    CliArgs,
    DatasetProfile,
)
from performance.query_plans.reports import write_reports
from performance.query_plans.runtime_capture import RuntimeQueryCapture
from performance.query_plans.scenarios import (
    STORAGE_SCENARIOS,
    StorageScenario,
    coverage_findings,
    evaluate_storage_method_coverage,
)
from performance.query_plans.seed import seed_profile, vacuum_analyze_seeded_tables
from performance.query_plans.sql import (
    compile_captured_query,
    group_queries_by_scenario,
    run_explain,
)


async def run_query_plan_profile(args: CliArgs) -> int:
    profile = get_profile(name=args.profile)
    ensure_safe_database_name(allow_non_test_db=args.allow_non_test_db)
    migrate(revision="heads")
    engine = create_async_engine(settings.database.url.get_secret_value(), poolclass=NullPool)
    coverage = evaluate_storage_method_coverage(
        discovered_methods=discover_storage_methods(),
        scenarios=STORAGE_SCENARIOS,
    )
    capture_findings: tuple[str, ...] = ()
    try:
        async with engine.begin() as connection:
            await seed_profile(connection=connection, profile=profile)
        async with engine.connect() as connection:
            autocommit_connection = await connection.execution_options(
                isolation_level="AUTOCOMMIT",
            )
            await vacuum_analyze_seeded_tables(connection=autocommit_connection)
        queries, capture_findings = await capture_storage_queries(
            engine=engine,
            scenarios=STORAGE_SCENARIOS,
        )
        async with engine.connect() as connection:
            results = await benchmark_queries(
                connection=connection,
                queries=queries,
                profile=profile,
            )
        write_reports(
            report_dir=args.report_dir,
            profile=profile,
            coverage=coverage,
            results=results,
        )
    finally:
        await engine.dispose()

    findings = (
        *coverage_findings(coverage=coverage),
        *capture_findings,
        *(finding for result in results for finding in result.findings),
    )
    stdout.write(f"Query plan report written to {args.report_dir}\n")
    if findings:
        stderr.write("\n".join(f"- {finding}" for finding in findings))
        stderr.write("\n")
        return 1 if args.fail_on_finding else 0
    return 0


async def capture_storage_queries(
    *,
    engine: AsyncEngine,
    scenarios: Sequence[StorageScenario],
) -> tuple[tuple[CapturedQuery, ...], tuple[str, ...]]:
    capture = RuntimeQueryCapture(clock=perf_counter_ns)
    capture.install(engine=engine)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    findings: list[str] = []

    for scenario in scenarios:
        stdout.write(f"Capturing SQL for {scenario.storage_class}.{scenario.method_name}\n")
        previous_query_count = len(capture.captured_queries)
        async with session_factory() as session:
            capture.start_scenario(
                storage_class=scenario.storage_class,
                method_name=scenario.method_name,
                scenario_name=scenario.name,
                expectation=scenario.plan_expectation(
                    policy=BALANCED_THRESHOLD_POLICY,
                    query_name=None,
                ),
            )
            try:
                await scenario.run(session)
            finally:
                capture.stop_scenario()
                await session.rollback()
        captured_count = len(capture.captured_queries) - previous_query_count
        if captured_count == 0:
            findings.append(f"{scenario.name}: storage scenario captured no SQL statements")

    return (
        apply_query_threshold_overrides(
            queries=capture.captured_queries,
            scenarios=scenarios,
        ),
        tuple(findings),
    )


def apply_query_threshold_overrides(
    *,
    queries: Sequence[CapturedQuery],
    scenarios: Sequence[StorageScenario],
) -> tuple[CapturedQuery, ...]:
    scenarios_by_name = {scenario.name: scenario for scenario in scenarios}
    return tuple(
        replace(
            query,
            expectation=scenarios_by_name[query.scenario_name].plan_expectation(
                policy=BALANCED_THRESHOLD_POLICY,
                query_name=query.name,
            ),
        )
        for query in queries
    )


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
    compiled_queries = {
        query.name: compile_captured_query(query=query, dialect=connection.dialect)
        for query in queries
    }
    explain_json_runs_by_query = {query.name: [] for query in queries}
    analyses_by_query = {query.name: [] for query in queries}
    for query in queries:
        stdout.write(f"Running EXPLAIN ANALYZE for {query.name}\n")
    query_groups = group_queries_by_scenario(queries)

    for _ in range(profile.explain_runs):
        for query_group in query_groups:
            transaction = await connection.begin()
            try:
                for query in query_group:
                    compiled_query = compiled_queries[query.name]
                    explain_json = await run_explain(
                        connection=connection,
                        compiled_query=compiled_query,
                    )
                    explain_json_runs_by_query[query.name].append(explain_json)
                    analyses_by_query[query.name].append(
                        analyze_explain_result(
                            name=query.name,
                            explain_json=cast("Sequence[object]", explain_json),
                            expectation=query.expectation,
                        ),
                    )
            finally:
                await transaction.rollback()

    results: list[BenchmarkResult] = []
    for query in queries:
        analyses = analyses_by_query[query.name]
        warm_execution_ms = median(analysis.execution_time_ms for analysis in analyses[1:])
        shape_findings = evaluate_plan_analysis(
            analysis=analyses[-1],
            expectation=query.expectation,
            measured_execution_ms=warm_execution_ms,
        )
        results.append(
            BenchmarkResult(
                query=query,
                compiled_query=compiled_queries[query.name],
                explain_json_runs=tuple(explain_json_runs_by_query[query.name]),
                analyses=tuple(analyses),
                warm_execution_ms=warm_execution_ms,
                findings=tuple(f"{query.name}: {finding}" for finding in shape_findings),
            ),
        )
    return tuple(results)
