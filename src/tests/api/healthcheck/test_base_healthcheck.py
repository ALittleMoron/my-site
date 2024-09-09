from httpx import codes

from tests.api.helpers import ApiFixture


class TestBaseHealthcheck(ApiFixture):
    def test_healthcheck(self) -> None:
        response = self.api.base_healthcheck()

        assert response.status_code == codes.OK
        assert response.text == ""
