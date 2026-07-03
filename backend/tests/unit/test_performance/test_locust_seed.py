from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError
from sqlalchemy.dialects import postgresql

from core.auth.enums import RoleEnum
from performance.locust.seed import (
    SEED_ARTICLE_FOLDER_ID,
    article_folder_row,
    article_range,
    article_tag_indexes,
    clear_seeded_data,
    insert_seed_user,
    validate_seed_config,
)
from performance.locust.settings import (
    LocustSeedConfig,
    LocustSeedDatabaseSettings,
    LocustSeedSettings,
)


class TestLocustPerformanceSeed:
    def test_seed_settings_require_explicit_seed_flag(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("PERFORMANCE_SEED_DATA", raising=False)

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

    def test_article_tag_indexes_are_unique_per_seeded_article(self) -> None:
        for article_index in article_range():
            indexes = article_tag_indexes(article_index=article_index)
            assert len(indexes) == len(set(indexes))

    def test_article_seed_rows_reference_normalized_folder(self) -> None:
        row = article_folder_row()

        assert row == {
            "id": "30000000000040008000000000000001",
            "key": "performance",
            "name_ru": "Производительность",
            "name_en": "Performance",
            "priority": 1,
        }

    async def test_seed_user_is_created_as_active_admin(self) -> None:
        session = AsyncMock()

        await insert_seed_user(session=session)

        statement = session.execute.await_args.args[0]
        compiled = statement.compile(dialect=postgresql.dialect())
        assert compiled.params["username"] == "performance-seed-admin"
        assert compiled.params["role"] == RoleEnum.ADMIN
        assert compiled.params["is_active"] is True

    async def test_clear_seeded_data_removes_query_plan_article_folder_collision(self) -> None:
        session = AsyncMock()

        await clear_seeded_data(session=session)

        statements = [call.args[0] for call in session.execute.await_args_list]
        folder_delete = next(
            statement
            for statement in statements
            if statement.table.name == "articles__article_folder_model"
        )
        compiled = folder_delete.compile(dialect=postgresql.dialect())

        assert SEED_ARTICLE_FOLDER_ID in compiled.params.values()
