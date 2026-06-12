import importlib.util

from dishka.integrations import taskiq as dishka_taskiq
from taskiq_redis import RedisAsyncResultBackend

from entrypoints.taskiq import broker as taskiq_broker_module
from entrypoints.taskiq import worker as taskiq_worker_module
from entrypoints.taskiq.cache_warm import tasks as cache_warm_tasks_module
from infra.config.constants import constants
from infra.config.settings import settings


class TestTaskiqBrokerConfiguration:
    def test_taskiq_uses_dedicated_valkey_databases(self) -> None:
        result_backend = taskiq_broker_module.broker.result_backend

        assert constants.valkey.databases.taskiq_broker == 3
        assert constants.valkey.databases.taskiq_results == 4
        assert (
            taskiq_broker_module.broker.connection_pool.connection_kwargs["db"]
            == constants.valkey.databases.taskiq_broker
        )
        assert isinstance(result_backend, RedisAsyncResultBackend)
        assert (
            result_backend.redis_pool.connection_kwargs["db"]
            == constants.valkey.databases.taskiq_results
        )

    def test_result_backend_uses_explicit_expiration_and_prefix(self) -> None:
        result_backend = taskiq_broker_module.broker.result_backend

        assert isinstance(result_backend, RedisAsyncResultBackend)
        assert result_backend.keep_results is True
        assert result_backend.result_ex_time == settings.taskiq.result_expire_seconds
        assert result_backend.prefix_str == constants.taskiq.result_prefix

    def test_broker_uses_expected_queue_and_consumer_group(self) -> None:
        assert taskiq_broker_module.broker.queue_name == constants.taskiq.queue_name
        assert (
            taskiq_broker_module.broker.consumer_group_name == constants.taskiq.consumer_group_name
        )
        assert taskiq_broker_module.broker.result_backend is not None

    def test_broker_module_does_not_export_one_line_configuration_helpers(self) -> None:
        for helper_name in (
            "TASKIQ_CONSUMER_GROUP_NAME",
            "TASKIQ_QUEUE_NAME",
            "TASKIQ_RESULT_PREFIX",
            "create_taskiq_broker",
            "create_taskiq_result_backend",
            "get_taskiq_broker_url",
            "get_taskiq_result_url",
            "get_taskiq_redis_url",
        ):
            assert not hasattr(taskiq_broker_module, helper_name)


class TestTaskiqScheduleConfiguration:
    def test_cache_warm_all_uses_interval_schedule_without_cron(self) -> None:
        schedule = cache_warm_tasks_module.cache_warm_all.labels["schedule"]

        assert schedule == [
            {
                "schedule_id": "cache_warm_all",
                "interval": settings.taskiq.cache_warm_interval_seconds,
            },
        ]
        assert "cron" not in schedule[0]

    def test_tasks_use_dishka_taskiq_middleware(self) -> None:
        assert any(
            isinstance(middleware, dishka_taskiq.ContainerMiddleware)
            for middleware in taskiq_broker_module.broker.middlewares
        )

    def test_worker_module_is_the_taskiq_registry_entrypoint(self) -> None:
        assert taskiq_worker_module.broker is taskiq_broker_module.broker
        assert taskiq_worker_module.scheduler.broker is taskiq_broker_module.broker
        assert (
            taskiq_worker_module.broker.find_task(constants.taskiq.cache_warm_all_task_name)
            is cache_warm_tasks_module.cache_warm_all
        )
        assert (
            taskiq_worker_module.broker.find_task(constants.taskiq.cache_warm_domain_task_name)
            is cache_warm_tasks_module.cache_warm_domain
        )

    def test_top_level_tasks_module_is_not_used_as_a_task_dumping_ground(self) -> None:
        assert importlib.util.find_spec("entrypoints.taskiq.tasks") is None
