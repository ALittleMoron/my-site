import os
from typing import Any

from locust import HttpUser, between, events, task

from infra.config.loggers import logger
from performance.locust.scenario import PublicSiteScenario
from performance.locust.thresholds import (
    PerformanceStats,
    evaluate_performance,
    thresholds_from_environment,
)


@events.quitting.add_listener
def enforce_performance_thresholds(environment: Any, **_kwargs: object) -> None:  # noqa: ANN401
    thresholds = thresholds_from_environment(os.environ)
    total = environment.stats.total
    stats = PerformanceStats(
        failure_ratio=total.fail_ratio,
        average_response_ms=total.avg_response_time,
        p95_response_ms=total.get_response_time_percentile(0.95),
    )
    violations = evaluate_performance(stats=stats, thresholds=thresholds)
    if total.num_requests == 0:
        violations = (*violations, "no requests were recorded")

    if violations:
        for violation in violations:
            logger.error("Performance threshold violated", violation=violation)
        environment.process_exit_code = 1
        return
    environment.process_exit_code = 0


class PublicSiteUser(HttpUser):
    wait_time = between(0.2, 1.0)
    scenario: PublicSiteScenario

    def on_start(self) -> None:
        self.scenario = PublicSiteScenario(client=self.client, environ=os.environ)

    @task(8)
    def healthcheck(self) -> None:
        self.scenario.healthcheck()

    @task(4)
    def i18n_languages(self) -> None:
        self.scenario.i18n_languages()

    @task(4)
    def i18n_bundle(self) -> None:
        self.scenario.i18n_bundle()

    @task(4)
    def notes_list(self) -> None:
        self.scenario.notes_list()

    @task(2)
    def notes_tree(self) -> None:
        self.scenario.notes_tree()

    @task(2)
    def note_detail(self) -> None:
        self.scenario.note_detail()

    @task(3)
    def matrix_sheets(self) -> None:
        self.scenario.matrix_sheets_task()

    @task(2)
    def matrix_items(self) -> None:
        self.scenario.matrix_items()

    @task(1)
    def matrix_resources_search(self) -> None:
        self.scenario.matrix_resources_search()

    @task(1)
    def spa_root(self) -> None:
        self.scenario.spa_root()
