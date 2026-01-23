from typing import Generator

import pytest

from config.settings import Settings


class TestSettings:
    @pytest.fixture(autouse=True)
    def setup(self, test_settings: Settings) -> Generator[None, None, None]:
        self.settings = test_settings
        orig = self.settings.app.domain
        self.settings.app.domain = "alittlemoron.ru"
        self.settings.app.schema = "https"
        yield
        self.settings.app.domain = orig
        self.settings.app.schema = "http"

    def test_base_url(self) -> None:
        assert self.settings.base_url == "https://alittlemoron.ru"

    def test_get_minio_object_url(self) -> None:
        assert (
            self.settings.get_minio_object_url(bucket="media", object_path="test.txt")
            == "https://s3.alittlemoron.ru/media/test.txt"
        )

    def test_get_minio_object_url_object_path_startswith_slash(self) -> None:
        assert (
            self.settings.get_minio_object_url(bucket="media", object_path="/test.txt")
            == "https://s3.alittlemoron.ru/media/test.txt"
        )

    def test_valkey_get_url(self) -> None:
        self.settings.valkey.host = "localhost"
        self.settings.valkey.port = 6379
        assert self.settings.valkey.get_url(db=0).get_secret_value() == "valkey://localhost:6379/0"
        assert (
            self.settings.valkey.url_for_http_cache.get_secret_value()
            == "valkey://localhost:6379/0"
        )
