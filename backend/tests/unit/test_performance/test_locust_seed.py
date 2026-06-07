import pytest
from pydantic import ValidationError

from performance.locust.seed import (
    note_range,
    note_tag_indexes,
    validate_seed_config,
)
from performance.locust.settings import (
    LocustSeedConfig,
    LocustSeedDatabaseSettings,
    LocustSeedSettings,
)


class TestLocustPerformanceSeed:
    def test_seed_settings_require_explicit_seed_flag(self) -> None:
        with pytest.raises(ValidationError, match="seed_data"):
            LocustSeedSettings(
                _env_file=None,
                host="http://127.0.0.1:8000",
            )

    def test_validate_seed_config_skips_disabled_seed(self) -> None:
        assert (
            validate_seed_config(
                LocustSeedConfig(
                    seed=LocustSeedSettings(
                        _env_file=None,
                        seed_data=False,
                        host="http://127.0.0.1:8000",
                    ),
                    database=LocustSeedDatabaseSettings(
                        _env_file=None,
                        host="localhost",
                        name="my_site_database_test",
                    ),
                ),
            )
            is False
        )

    def test_validate_seed_config_allows_local_test_database(self) -> None:
        assert (
            validate_seed_config(
                LocustSeedConfig(
                    seed=LocustSeedSettings(
                        _env_file=None,
                        seed_data=True,
                        host="http://127.0.0.1:8000",
                    ),
                    database=LocustSeedDatabaseSettings(
                        _env_file=None,
                        host="localhost",
                        name="my_site_database_test",
                    ),
                ),
            )
            is True
        )

    def test_validate_seed_config_rejects_enabled_non_test_database(self) -> None:
        with pytest.raises(ValueError, match="PERFORMANCE_SEED_DATA requires a test database"):
            validate_seed_config(
                LocustSeedConfig(
                    seed=LocustSeedSettings(
                        _env_file=None,
                        seed_data=True,
                        host="http://127.0.0.1:8000",
                    ),
                    database=LocustSeedDatabaseSettings(
                        _env_file=None,
                        host="localhost",
                        name="my_site_database",
                    ),
                ),
            )

    def test_validate_seed_config_rejects_enabled_remote_target(self) -> None:
        with pytest.raises(ValueError, match="PERFORMANCE_SEED_DATA requires a local target"):
            validate_seed_config(
                LocustSeedConfig(
                    seed=LocustSeedSettings(
                        _env_file=None,
                        seed_data=True,
                        host="https://example.com",
                    ),
                    database=LocustSeedDatabaseSettings(
                        _env_file=None,
                        host="localhost",
                        name="my_site_database_test",
                    ),
                ),
            )

    def test_seed_settings_parse_environment_values(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("PERFORMANCE_SEED_DATA", "true")
        monkeypatch.setenv("PERFORMANCE_HOST", "http://127.0.0.1:8000")
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_NAME", "my_site_database_test")

        settings = LocustSeedSettings(
            _env_file=None,
        )

        assert settings.seed_data is True
        assert settings.host == "http://127.0.0.1:8000"

    def test_seed_database_settings_parse_database_prefixed_environment_values(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_NAME", "my_site_database_test")

        settings = LocustSeedDatabaseSettings(
            _env_file=None,
        )

        assert settings.host == "localhost"
        assert settings.name == "my_site_database_test"

    def test_note_tag_indexes_are_unique_per_seeded_note(self) -> None:
        for note_index in note_range():
            indexes = note_tag_indexes(note_index=note_index)
            assert len(indexes) == len(set(indexes))
