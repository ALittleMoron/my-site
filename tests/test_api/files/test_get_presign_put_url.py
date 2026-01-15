import pytest_asyncio
from httpx import codes

from core.auth.schemas import JwtUser
from tests.fixtures import ApiFixture, FactoryFixture, ContainerFixture


class TestGetPresignPutUrlAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, jwt_user: JwtUser, jwt_admin: JwtUser) -> None:
        self.user = jwt_user
        self.admin = jwt_admin
        self.authentication_use_case = await self.container.get_authenticate_use_case()
        self.use_case = await self.container.get_presign_put_url_use_case()

    def test_get_presign_put_url_admin_permission(self) -> None:
        self.authentication_use_case.execute.return_value = self.user
        response = self.api.get_presign_put_url(content_type="image/png")
        assert response.status_code == codes.UNAUTHORIZED

    def test_get_presign_put_url(self) -> None:
        self.authentication_use_case.execute.return_value = self.admin
        self.api.get_presign_put_url(content_type="image/png")
        self.use_case.execute.assert_called_once_with(
            params=self.factory.core.presign_put_object_params(
                content_type="image/png",
                folder="text-attachments",
                namespace="media",
            ),
        )
