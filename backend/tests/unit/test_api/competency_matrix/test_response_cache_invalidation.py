import pytest
import pytest_asyncio
from httpx import codes

from core.enums import PublishStatusEnum
from entrypoints.litestar.response_cache import ResponseCacheDomain
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestCompetencyMatrixResponseCacheInvalidation(
    ContainerFixture,
    ApiFixture,
    FactoryFixture,
):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_competency_matrix_use_case()

    def test_successful_item_mutations_invalidate_matrix_response_cache(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        invalidated_domains: list[ResponseCacheDomain] = []

        async def fake_invalidate_response_cache_domain(
            *,
            request: object,
            domain: ResponseCacheDomain,
        ) -> None:
            _ = request
            invalidated_domains.append(domain)

        monkeypatch.setattr(
            "entrypoints.litestar.api.competency_matrix.endpoints.invalidate_response_cache_domain",
            fake_invalidate_response_cache_domain,
            raising=False,
        )
        self.use_case.create_item.return_value = self.factory.core.competency_matrix_item(
            item_id=1,
            publish_status=PublishStatusEnum.DRAFT,
        )
        self.use_case.update_item.return_value = self.factory.core.competency_matrix_item(
            item_id=1,
            publish_status=PublishStatusEnum.PUBLISHED,
        )

        responses = [
            self.api.post_create_item(data=self.factory.api.competency_matrix_item_request()),
            self.api.put_update_item(pk=1, data=self.factory.api.competency_matrix_item_request()),
            self.api.delete_item(pk=1),
            self.api.post_set_published_status_to_item(pk=1),
            self.api.post_set_draft_status_to_item(pk=1),
        ]

        assert [response.status_code for response in responses] == [
            codes.CREATED,
            codes.OK,
            codes.NO_CONTENT,
            codes.NO_CONTENT,
            codes.NO_CONTENT,
        ]
        assert invalidated_domains == [ResponseCacheDomain.COMPETENCY_MATRIX] * 5

    def test_item_validation_error_does_not_invalidate_matrix_response_cache(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        invalidated_domains: list[ResponseCacheDomain] = []

        async def fake_invalidate_response_cache_domain(
            *,
            request: object,
            domain: ResponseCacheDomain,
        ) -> None:
            _ = request
            invalidated_domains.append(domain)

        monkeypatch.setattr(
            "entrypoints.litestar.api.competency_matrix.endpoints.invalidate_response_cache_domain",
            fake_invalidate_response_cache_domain,
            raising=False,
        )

        response = self.api.post_create_item(
            data=self.factory.api.competency_matrix_item_request(),
            language=None,
        )

        assert response.status_code == codes.BAD_REQUEST
        assert invalidated_domains == []
