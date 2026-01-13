import pytest_asyncio

from tests.fixtures import ApiFixture, FactoryFixture, ContainerFixture


class TestGetPresignPutUrlAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_presign_put_url_use_case()

    def test_get_presign_put_url(self) -> None:
        self.api.get_presign_put_url(content_type="image/png")
        self.use_case.execute.assert_called_once_with(
            params=self.factory.core.presign_put_object_params(
                content_type="image/png",
                folder="text-attachments",
                namespace="media",
            ),
        )
