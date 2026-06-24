import pytest_asyncio
from httpx import codes

from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from tests.test_cases import ApiTestCase


class TestGetPresignPutUrlAPI(ApiTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, jwt_user: JwtUser, jwt_admin: JwtUser) -> None:
        self.user = jwt_user
        self.admin = jwt_admin
        self.authentication_use_case = await self.container.get_auth_use_case()
        self.use_case = await self.container.get_files_use_case()
        self.use_case.presign_put_object.return_value = self.factory.core.presign_put_object(
            upload_url="http://localhost/upload",
            access_url="http://localhost/access",
        )

    def test_get_presign_put_url_admin_permission(self) -> None:
        self.authentication_use_case.authenticate.return_value = self.user
        response = self.api.get_presign_put_url(content_type="image/png")
        assert response.status_code == codes.UNAUTHORIZED

    def test_get_presign_put_url_moderator_permission(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="moderator",
            role=RoleEnum.MODERATOR,
        )
        response = self.api.get_presign_put_url(content_type="image/png")

        assert response.status_code == codes.OK, response.content
        self.use_case.presign_put_object.assert_called_once_with(
            params=self.factory.core.presign_put_object_params(
                content_type="image/png",
                folder="text-attachments",
                namespace="media",
            ),
        )

    def test_get_presign_put_url(self) -> None:
        self.authentication_use_case.authenticate.return_value = self.admin
        self.api.get_presign_put_url(content_type="image/png")
        self.use_case.presign_put_object.assert_called_once_with(
            params=self.factory.core.presign_put_object_params(
                content_type="image/png",
                folder="text-attachments",
                namespace="media",
            ),
        )
