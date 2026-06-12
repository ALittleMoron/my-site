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

    def test_successful_item_mutations_enqueue_matrix_response_cache_warm(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        warmed_domains: list[ResponseCacheDomain] = []

        async def fake_invalidate_and_enqueue_response_cache_warm_domain(
            *,
            request: object,
            domain: ResponseCacheDomain,
        ) -> None:
            _ = request
            warmed_domains.append(domain)

        monkeypatch.setattr(
            "entrypoints.litestar.api.competency_matrix.endpoints.invalidate_and_enqueue_response_cache_warm_domain",
            fake_invalidate_and_enqueue_response_cache_warm_domain,
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
        self.use_case.create_item_from_queue.return_value = (
            self.factory.core.competency_matrix_item(
                item_id=2,
                publish_status=PublishStatusEnum.DRAFT,
            )
        )

        responses = [
            self.api.post_create_item(data=self.factory.api.competency_matrix_item_request()),
            self.api.post_create_item_from_queue(
                question_id=1,
                data=self.factory.api.competency_matrix_item_request(slug="queued-question"),
            ),
            self.api.put_update_item(pk=1, data=self.factory.api.competency_matrix_item_request()),
            self.api.delete_item(pk=1),
            self.api.post_set_published_status_to_item(pk=1),
            self.api.post_set_draft_status_to_item(pk=1),
        ]

        assert [response.status_code for response in responses] == [
            codes.CREATED,
            codes.CREATED,
            codes.OK,
            codes.NO_CONTENT,
            codes.NO_CONTENT,
            codes.NO_CONTENT,
        ]
        assert warmed_domains == [ResponseCacheDomain.COMPETENCY_MATRIX] * 6

    def test_item_validation_error_does_not_enqueue_matrix_response_cache_warm(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        warmed_domains: list[ResponseCacheDomain] = []

        async def fake_invalidate_and_enqueue_response_cache_warm_domain(
            *,
            request: object,
            domain: ResponseCacheDomain,
        ) -> None:
            _ = request
            warmed_domains.append(domain)

        monkeypatch.setattr(
            "entrypoints.litestar.api.competency_matrix.endpoints.invalidate_and_enqueue_response_cache_warm_domain",
            fake_invalidate_and_enqueue_response_cache_warm_domain,
            raising=False,
        )

        response = self.api.post_create_item(
            data=self.factory.api.competency_matrix_item_request(),
            language=None,
        )

        assert response.status_code == codes.BAD_REQUEST
        assert warmed_domains == []
