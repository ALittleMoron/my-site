from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PerformanceStats:
    failure_ratio: float
    average_response_ms: float
    p95_response_ms: float


@dataclass(frozen=True, slots=True)
class PerformanceThresholds:
    max_failure_ratio: float
    max_average_response_ms: float
    max_p95_response_ms: float


def thresholds_from_environment(environ: Mapping[str, str]) -> PerformanceThresholds:
    return PerformanceThresholds(
        max_failure_ratio=read_float(environ=environ, key="LOCUST_MAX_FAILURE_RATIO"),
        max_average_response_ms=read_float(environ=environ, key="LOCUST_MAX_AVG_RESPONSE_MS"),
        max_p95_response_ms=read_float(environ=environ, key="LOCUST_MAX_P95_RESPONSE_MS"),
    )


def evaluate_performance(
    *,
    stats: PerformanceStats,
    thresholds: PerformanceThresholds,
) -> tuple[str, ...]:
    violations: list[str] = []
    if stats.failure_ratio > thresholds.max_failure_ratio:
        violations.append(
            f"failure ratio {stats.failure_ratio:.2%} exceeded threshold "
            f"{thresholds.max_failure_ratio:.2%}",
        )
    if stats.average_response_ms > thresholds.max_average_response_ms:
        violations.append(
            f"average response time {stats.average_response_ms:.2f} ms exceeded threshold "
            f"{thresholds.max_average_response_ms:.2f} ms",
        )
    if stats.p95_response_ms > thresholds.max_p95_response_ms:
        violations.append(
            f"p95 response time {stats.p95_response_ms:.2f} ms exceeded threshold "
            f"{thresholds.max_p95_response_ms:.2f} ms",
        )
    return tuple(violations)


def read_float(*, environ: Mapping[str, str], key: str) -> float:
    try:
        raw_value = environ[key]
    except KeyError as exc:
        msg = f"{key} is required"
        raise ValueError(msg) from exc
    try:
        return float(raw_value)
    except ValueError as exc:
        msg = f"{key} must be a number"
        raise ValueError(msg) from exc
