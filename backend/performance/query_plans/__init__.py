from collections.abc import Awaitable, Callable
from importlib import import_module
from typing import cast

from performance.query_plans.analysis import analyze_explain_result
from performance.query_plans.capture import capture_balanced_queries
from performance.query_plans.models import (
    BenchmarkResult,
    CapturedQuery,
    CliArgs,
    CompiledQuery,
    DatasetProfile,
    PlanAnalysis,
    PlanExpectation,
)
from performance.query_plans.seed import generate_series_subquery
from performance.query_plans.sql import compile_captured_query


async def run_query_plan_profile(args: CliArgs) -> int:
    runner = import_module("performance.query_plans.runner")
    run_profile = cast(
        "Callable[[CliArgs], Awaitable[int]]",
        runner.run_query_plan_profile,
    )
    return await run_profile(args)


__all__ = (
    "BenchmarkResult",
    "CapturedQuery",
    "CliArgs",
    "CompiledQuery",
    "DatasetProfile",
    "PlanAnalysis",
    "PlanExpectation",
    "analyze_explain_result",
    "capture_balanced_queries",
    "compile_captured_query",
    "generate_series_subquery",
    "run_query_plan_profile",
)
