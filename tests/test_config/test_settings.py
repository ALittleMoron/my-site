import pytest

from config.settings import Settings


class TestSettings:
    @pytest.fixture(autouse=True)
    def setup(self, test_settings: Settings) -> None:
        self.settings = test_settings
        self.settings.app.domain = "alittlemoron.ru"

    def test_base_url(self) -> None:
        assert self.settings.base_url == "https://alittlemoron.ru"

    def test_get_minio_object_url(self) -> None:
        assert (
            self.settings.get_minio_object_url(bucket="media", object_path="test.txt")
            == "https://alittlemoron.ru/media/test.txt"
        )

    def test_get_minio_object_url_object_path_startswith_slash(self) -> None:
        assert (
            self.settings.get_minio_object_url(bucket="media", object_path="/test.txt")
            == "https://alittlemoron.ru/media/test.txt"
        )
