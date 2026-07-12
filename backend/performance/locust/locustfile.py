from typing import Any

from locust import HttpUser, between, events, task

from infra.config.loggers import logger
from performance.locust.constants import constants
from performance.locust.scenario import PublicSiteScenario
from performance.locust.settings import settings
from performance.locust.thresholds import (
    PerformanceStats,
    evaluate_performance,
    thresholds_from_settings,
)


@events.quitting.add_listener
def enforce_performance_thresholds(environment: Any, **_kwargs: object) -> None:  # noqa: ANN401
    thresholds = thresholds_from_settings(settings.thresholds)
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
    wait_time = between(constants.wait_time.min_seconds, constants.wait_time.max_seconds)
    scenario: PublicSiteScenario

    def on_start(self) -> None:
        self.scenario = PublicSiteScenario(
            client=self.client,
            settings=settings.scenario,
        )

    @task(constants.task_weights.healthcheck)
    def healthcheck(self) -> None:
        self.scenario.healthcheck()

    @task(constants.task_weights.i18n_languages)
    def i18n_languages(self) -> None:
        self.scenario.i18n_languages()

    @task(constants.task_weights.i18n_bundle)
    def i18n_bundle(self) -> None:
        self.scenario.i18n_bundle()

    @task(constants.task_weights.articles_list)
    def articles_list(self) -> None:
        self.scenario.articles_list()

    @task(constants.task_weights.articles_tree)
    def articles_tree(self) -> None:
        self.scenario.articles_tree()

    @task(constants.task_weights.article_detail)
    def article_detail(self) -> None:
        self.scenario.article_detail()

    @task(constants.task_weights.matrix_sheets)
    def matrix_sheets(self) -> None:
        self.scenario.matrix_sheets_task()

    @task(constants.task_weights.matrix_items)
    def matrix_items(self) -> None:
        self.scenario.matrix_items()

    @task(constants.task_weights.matrix_item_detail)
    def matrix_item_detail(self) -> None:
        self.scenario.matrix_item_detail()

    @task(constants.task_weights.matrix_question_suggestion)
    def matrix_question_suggestion(self) -> None:
        self.scenario.matrix_question_suggestion()

    @task(constants.task_weights.spa_root)
    def spa_root(self) -> None:
        self.scenario.spa_root()
