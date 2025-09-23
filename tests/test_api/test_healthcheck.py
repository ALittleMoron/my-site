from verbose_http_exceptions import status

from tests.fixtures import ApiFixture


class TestHealthCheckAPI(ApiFixture):
    def test_healthcheck(self) -> None:
        response = self.api.get_health()
        assert response.status_code == status.HTTP_200_OK
