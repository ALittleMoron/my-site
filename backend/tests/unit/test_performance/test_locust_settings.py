import pytest
from pydantic import ValidationError

from core.i18n.enums import LanguageEnum
from performance.locust.settings import (
    LocustScenarioSettings,
    LocustSettings,
    LocustThresholdSettings,
    settings,
)


class TestLocustSettings:
    def test_global_settings_is_single_locust_settings_instance(self) -> None:
        assert isinstance(settings, LocustSettings)

    def test_scenario_settings_require_explicit_values(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("PERFORMANCE_LANGUAGE", raising=False)

        with pytest.raises(ValidationError, match="language"):
            LocustScenarioSettings(
                _env_file=None,
                include_spa=False,
                include_matrix_suggestions=False,
                validate_responses=True,
            )

    def test_scenario_settings_parse_environment_values(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("PERFORMANCE_LANGUAGE", "ru")
        monkeypatch.setenv("PERFORMANCE_INCLUDE_SPA", "false")
        monkeypatch.setenv("PERFORMANCE_INCLUDE_MATRIX_SUGGESTIONS", "true")
        monkeypatch.setenv("PERFORMANCE_VALIDATE_RESPONSES", "true")

        settings = LocustScenarioSettings(
            _env_file=None,
        )

        assert settings.language == LanguageEnum.RU
        assert settings.include_spa is False
        assert settings.include_matrix_suggestions is True
        assert settings.validate_responses is True

    def test_threshold_settings_require_explicit_values(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("LOCUST_MAX_FAILURE_RATIO", raising=False)

        with pytest.raises(ValidationError, match="max_failure_ratio"):
            LocustThresholdSettings(
                _env_file=None,
                max_avg_response_ms=50.0,
                max_p95_response_ms=75.0,
            )

    def test_threshold_settings_parse_environment_values(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("LOCUST_MAX_FAILURE_RATIO", "0.0")
        monkeypatch.setenv("LOCUST_MAX_AVG_RESPONSE_MS", "50")
        monkeypatch.setenv("LOCUST_MAX_P95_RESPONSE_MS", "75")

        settings = LocustThresholdSettings(
            _env_file=None,
        )

        assert settings.max_failure_ratio == 0.0
        assert settings.max_avg_response_ms == 50.0
        assert settings.max_p95_response_ms == 75.0

    def test_locust_settings_builds_prefixed_sections(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("PERFORMANCE_LANGUAGE", "en")
        monkeypatch.setenv("PERFORMANCE_INCLUDE_SPA", "false")
        monkeypatch.setenv("PERFORMANCE_INCLUDE_MATRIX_SUGGESTIONS", "true")
        monkeypatch.setenv("PERFORMANCE_VALIDATE_RESPONSES", "true")
        monkeypatch.setenv("PERFORMANCE_SEED_DATA", "true")
        monkeypatch.setenv("PERFORMANCE_HOST", "http://127.0.0.1:8000")
        monkeypatch.setenv("LOCUST_MAX_FAILURE_RATIO", "0.0")
        monkeypatch.setenv("LOCUST_MAX_AVG_RESPONSE_MS", "50")
        monkeypatch.setenv("LOCUST_MAX_P95_RESPONSE_MS", "75")
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_NAME", "my_site_database_test")

        locust_settings = LocustSettings()

        assert locust_settings.scenario.language == LanguageEnum.EN
        assert locust_settings.thresholds.max_avg_response_ms == 50.0
        assert locust_settings.seed.seed.seed_data is True
        assert locust_settings.seed.database.name == "my_site_database_test"
