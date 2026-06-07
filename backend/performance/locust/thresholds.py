from dataclasses import dataclass

from performance.locust.settings import LocustThresholdSettings


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


def thresholds_from_settings(settings: LocustThresholdSettings) -> PerformanceThresholds:
    return PerformanceThresholds(
        max_failure_ratio=settings.max_failure_ratio,
        max_average_response_ms=settings.max_avg_response_ms,
        max_p95_response_ms=settings.max_p95_response_ms,
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
