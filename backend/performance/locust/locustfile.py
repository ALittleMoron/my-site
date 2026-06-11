from typing import Any

from locust import HttpUser, between, events, task

from infra.config.loggers import logger
from performance.locust import constants
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
    wait_time = between(constants.WAIT_TIME_MIN_SECONDS, constants.WAIT_TIME_MAX_SECONDS)
    scenario: PublicSiteScenario

    def on_start(self) -> None:
        self.scenario = PublicSiteScenario(
            client=self.client,
            settings=settings.scenario,
        )

    @task(constants.TASK_WEIGHT_HEALTHCHECK)
    def healthcheck(self) -> None:
        self.scenario.healthcheck()

    @task(constants.TASK_WEIGHT_I18N_LANGUAGES)
    def i18n_languages(self) -> None:
        self.scenario.i18n_languages()

    @task(constants.TASK_WEIGHT_I18N_BUNDLE)
    def i18n_bundle(self) -> None:
        self.scenario.i18n_bundle()

    @task(constants.TASK_WEIGHT_NOTES_LIST)
    def notes_list(self) -> None:
        self.scenario.notes_list()

    @task(constants.TASK_WEIGHT_NOTES_TREE)
    def notes_tree(self) -> None:
        self.scenario.notes_tree()

    @task(constants.TASK_WEIGHT_NOTE_DETAIL)
    def note_detail(self) -> None:
        self.scenario.note_detail()

    @task(constants.TASK_WEIGHT_MATRIX_SHEETS)
    def matrix_sheets(self) -> None:
        self.scenario.matrix_sheets_task()

    @task(constants.TASK_WEIGHT_MATRIX_ITEMS)
    def matrix_items(self) -> None:
        self.scenario.matrix_items()

    @task(constants.TASK_WEIGHT_MATRIX_ITEM_DETAIL)
    def matrix_item_detail(self) -> None:
        self.scenario.matrix_item_detail()

    @task(constants.TASK_WEIGHT_MATRIX_QUESTION_SUGGESTION)
    def matrix_question_suggestion(self) -> None:
        self.scenario.matrix_question_suggestion()

    @task(constants.TASK_WEIGHT_SPA_ROOT)
    def spa_root(self) -> None:
        self.scenario.spa_root()
