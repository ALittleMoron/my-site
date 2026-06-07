from performance.locust.settings import LocustThresholdSettings
from performance.locust.thresholds import (
    PerformanceStats,
    PerformanceThresholds,
    evaluate_performance,
    thresholds_from_settings,
)


class TestPerformanceThresholds:
    def test_thresholds_from_settings_maps_explicit_values(self) -> None:
        thresholds = thresholds_from_settings(
            LocustThresholdSettings(
                _env_file=None,
                max_failure_ratio=0.0,
                max_avg_response_ms=50.0,
                max_p95_response_ms=75.0,
            ),
        )

        assert thresholds == PerformanceThresholds(
            max_failure_ratio=0.0,
            max_average_response_ms=50.0,
            max_p95_response_ms=75.0,
        )

    def test_evaluate_performance_returns_no_violations_inside_thresholds(self) -> None:
        violations = evaluate_performance(
            stats=PerformanceStats(
                failure_ratio=0.0,
                average_response_ms=49.0,
                p95_response_ms=74.0,
            ),
            thresholds=PerformanceThresholds(
                max_failure_ratio=0.0,
                max_average_response_ms=50.0,
                max_p95_response_ms=75.0,
            ),
        )

        assert violations == ()

    def test_evaluate_performance_reports_each_threshold_violation(self) -> None:
        violations = evaluate_performance(
            stats=PerformanceStats(
                failure_ratio=0.01,
                average_response_ms=51.0,
                p95_response_ms=76.0,
            ),
            thresholds=PerformanceThresholds(
                max_failure_ratio=0.0,
                max_average_response_ms=50.0,
                max_p95_response_ms=75.0,
            ),
        )

        assert violations == (
            "failure ratio 1.00% exceeded threshold 0.00%",
            "average response time 51.00 ms exceeded threshold 50.00 ms",
            "p95 response time 76.00 ms exceeded threshold 75.00 ms",
        )
