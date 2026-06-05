import pytest

from performance.locust.seed import (
    PerformanceSeedConfig,
    note_range,
    note_tag_indexes,
    seed_config_from_environment,
    validate_seed_config,
)


class TestLocustPerformanceSeed:
    def test_seed_config_from_environment_requires_explicit_seed_flag(self) -> None:
        with pytest.raises(ValueError, match="PERFORMANCE_SEED_DATA"):
            seed_config_from_environment({})

    def test_validate_seed_config_skips_disabled_seed(self) -> None:
        assert (
            validate_seed_config(
                PerformanceSeedConfig(
                    enabled=False,
                    performance_host="http://127.0.0.1:8000",
                    db_host="localhost",
                    db_name="my_site_database_test",
                ),
            )
            is False
        )

    def test_validate_seed_config_allows_local_test_database(self) -> None:
        assert (
            validate_seed_config(
                PerformanceSeedConfig(
                    enabled=True,
                    performance_host="http://127.0.0.1:8000",
                    db_host="localhost",
                    db_name="my_site_database_test",
                ),
            )
            is True
        )

    def test_validate_seed_config_rejects_enabled_non_test_database(self) -> None:
        with pytest.raises(ValueError, match="PERFORMANCE_SEED_DATA requires a test database"):
            validate_seed_config(
                PerformanceSeedConfig(
                    enabled=True,
                    performance_host="http://127.0.0.1:8000",
                    db_host="localhost",
                    db_name="my_site_database",
                ),
            )

    def test_validate_seed_config_rejects_enabled_remote_target(self) -> None:
        with pytest.raises(ValueError, match="PERFORMANCE_SEED_DATA requires a local target"):
            validate_seed_config(
                PerformanceSeedConfig(
                    enabled=True,
                    performance_host="https://example.com",
                    db_host="localhost",
                    db_name="my_site_database_test",
                ),
            )

    def test_seed_config_from_environment_parses_explicit_values(self) -> None:
        assert seed_config_from_environment(
            {
                "PERFORMANCE_SEED_DATA": "true",
                "PERFORMANCE_HOST": "http://127.0.0.1:8000",
                "DB_HOST": "localhost",
                "DB_NAME": "my_site_database_test",
            },
        ) == PerformanceSeedConfig(
            enabled=True,
            performance_host="http://127.0.0.1:8000",
            db_host="localhost",
            db_name="my_site_database_test",
        )

    def test_note_tag_indexes_are_unique_per_seeded_note(self) -> None:
        for note_index in note_range():
            indexes = note_tag_indexes(note_index=note_index)
            assert len(indexes) == len(set(indexes))
