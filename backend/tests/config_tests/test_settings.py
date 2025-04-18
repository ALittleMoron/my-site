import pytest

from config.settings import Settings


class TestSettings:
    @pytest.fixture(autouse=True)
    def setup(self, test_settings: Settings) -> None:
        self.settings = test_settings
        self.settings.minio.secure = False
        self.settings.app.domain_host = "alittlemoron.ru"

    def test_minio_url_localhost_with_port(self) -> None:
        self.settings.minio.port = 12567
        self.settings.app.domain_host = "localhost"
        assert self.settings.minio_url == "http://localhost:12567"

    def test_minio_url(self) -> None:
        assert self.settings.minio_url == "http://alittlemoron.ru/minio"

    def test_get_minio_object_url(self) -> None:
        assert (
            self.settings.get_minio_object_url(bucket="media", object_path="test.txt")
            == "http://alittlemoron.ru/minio/media/test.txt"
        )

    def test_get_minio_object_url_object_path_startswith_slash(self) -> None:
        assert (
            self.settings.get_minio_object_url(bucket="media", object_path="/test.txt")
            == "http://alittlemoron.ru/minio/media/test.txt"
        )
