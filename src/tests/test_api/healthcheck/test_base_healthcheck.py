from httpx import codes

from tests.fixtures import ApiFixture


class TestBaseHealthcheck(ApiFixture):
    def test_healthcheck(self) -> None:
        response = self.mocked_api.base_healthcheck()

        assert response.status_code == codes.OK
        assert response.text == ""
