from httpx import codes

from tests.fixtures import ApiFixture, FactoryFixture, ContainerFixture


class TestGetBaseCurrentUserAccountAPI(ContainerFixture, ApiFixture, FactoryFixture):
    async def test_get_base_current_user_account(self) -> None:
        response = self.api.get_get_base_current_user_account()
        assert response.status_code == codes.OK
        assert response.json() == {"username": "test", "role": "admin"}
