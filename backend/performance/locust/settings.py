from dataclasses import dataclass
from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.i18n.enums import LanguageEnum
from infra.config.constants import constants


class LocustBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=constants.path.env_file, extra="ignore")


class LocustScenarioSettings(LocustBaseSettings):
    model_config = SettingsConfigDict(env_prefix="PERFORMANCE_")

    language: LanguageEnum
    include_spa: bool
    include_matrix_suggestions: bool
    validate_responses: bool
    seed_data: bool


class LocustThresholdSettings(LocustBaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOCUST_")

    max_failure_ratio: float
    max_avg_response_ms: float
    max_p95_response_ms: float


class LocustSeedSettings(LocustBaseSettings):
    model_config = SettingsConfigDict(env_prefix="PERFORMANCE_")

    seed_data: bool
    host: str


class LocustSeedDatabaseSettings(LocustBaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LocustSeedConfig:
    seed: LocustSeedSettings
    database: LocustSeedDatabaseSettings


@dataclass(frozen=True)
class LocustSettings:
    @cached_property
    def scenario(self) -> LocustScenarioSettings:
        return LocustScenarioSettings()

    @cached_property
    def thresholds(self) -> LocustThresholdSettings:
        return LocustThresholdSettings()

    @cached_property
    def seed(self) -> LocustSeedConfig:
        return LocustSeedConfig(
            seed=LocustSeedSettings(),
            database=LocustSeedDatabaseSettings(),
        )


settings = LocustSettings()
