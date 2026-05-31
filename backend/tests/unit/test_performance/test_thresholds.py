import pytest

from performance.locust.thresholds import (
    PerformanceStats,
    PerformanceThresholds,
    evaluate_performance,
    thresholds_from_environment,
)


class TestPerformanceThresholds:
    def test_thresholds_from_environment_requires_failure_ratio(self) -> None:
        with pytest.raises(ValueError, match="LOCUST_MAX_FAILURE_RATIO"):
            thresholds_from_environment({})

    def test_thresholds_from_environment_parses_explicit_values(self) -> None:
        thresholds = thresholds_from_environment(
            {
                "LOCUST_MAX_FAILURE_RATIO": "0.02",
                "LOCUST_MAX_AVG_RESPONSE_MS": "1000",
                "LOCUST_MAX_P95_RESPONSE_MS": "2500",
            },
        )

        assert thresholds == PerformanceThresholds(
            max_failure_ratio=0.02,
            max_average_response_ms=1000.0,
            max_p95_response_ms=2500.0,
        )

    def test_evaluate_performance_returns_no_violations_inside_thresholds(self) -> None:
        violations = evaluate_performance(
            stats=PerformanceStats(
                failure_ratio=0.01,
                average_response_ms=900.0,
                p95_response_ms=2400.0,
            ),
            thresholds=PerformanceThresholds(
                max_failure_ratio=0.02,
                max_average_response_ms=1000.0,
                max_p95_response_ms=2500.0,
            ),
        )

        assert violations == ()

    def test_evaluate_performance_reports_each_threshold_violation(self) -> None:
        violations = evaluate_performance(
            stats=PerformanceStats(
                failure_ratio=0.03,
                average_response_ms=1001.0,
                p95_response_ms=2501.0,
            ),
            thresholds=PerformanceThresholds(
                max_failure_ratio=0.02,
                max_average_response_ms=1000.0,
                max_p95_response_ms=2500.0,
            ),
        )

        assert violations == (
            "failure ratio 3.00% exceeded threshold 2.00%",
            "average response time 1001.00 ms exceeded threshold 1000.00 ms",
            "p95 response time 2501.00 ms exceeded threshold 2500.00 ms",
        )
