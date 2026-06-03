from datetime import UTC, datetime

import pytest_asyncio
from httpx import codes

from core.enums import PublishStatusEnum
from core.notes.schemas import PublishedNoteForSeo
from tests.unit.fixtures import ApiFixture, ContainerFixture


class TestSeoDiscoveryAPI(ContainerFixture, ApiFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_notes_use_case()

    def test_sitemap_contains_language_prefixed_public_pages_and_published_notes(self) -> None:
        note = PublishedNoteForSeo(
            slug="typed-notes",
            publish_status=PublishStatusEnum.PUBLISHED,
            updated_at=datetime(2026, 2, 4, 4, 5, 6, tzinfo=UTC),
        )
        self.use_case.list_published_notes_for_seo.return_value = [note]

        response = self.no_auth_api.get_sitemap_xml()

        assert response.status_code == codes.OK, response.content
        assert response.headers["content-type"].startswith("application/xml")
        sitemap = response.text
        assert "<loc>http://localhost:8000/ru/about-me</loc>" in sitemap
        assert "<loc>http://localhost:8000/en/about-me</loc>" in sitemap
        assert "<loc>http://localhost:8000/ru/notes/typed-notes</loc>" in sitemap
        assert "<loc>http://localhost:8000/en/notes/typed-notes</loc>" in sitemap
        assert 'hreflang="ru" href="http://localhost:8000/ru/notes/typed-notes"' in sitemap
        assert 'hreflang="en" href="http://localhost:8000/en/notes/typed-notes"' in sitemap
        assert "<lastmod>2026-02-04T04:05:06+00:00</lastmod>" in sitemap
        assert "/competency-matrix/" not in sitemap
        self.use_case.list_published_notes_for_seo.assert_called_once_with()

    def test_sitemap_skips_draft_notes_returned_by_storage_defensively(self) -> None:
        draft = PublishedNoteForSeo(
            slug="draft-note",
            publish_status=PublishStatusEnum.DRAFT,
            updated_at=datetime(2026, 2, 4, 4, 5, 6, tzinfo=UTC),
        )
        self.use_case.list_published_notes_for_seo.return_value = [draft]

        response = self.no_auth_api.get_sitemap_xml()

        assert response.status_code == codes.OK, response.content
        assert "/notes/draft-note" not in response.text

    def test_robots_allows_public_language_routes_and_blocks_duplicate_spa_routes(self) -> None:
        response = self.no_auth_api.get_robots_txt()

        assert response.status_code == codes.OK, response.content
        assert response.headers["content-type"].startswith("text/plain")
        assert response.text == (
            "User-agent: *\n"
            "Allow: /ru/\n"
            "Allow: /en/\n"
            "Allow: /sitemap.xml\n"
            "Disallow: /api/\n"
            "Disallow: /login\n"
            "Disallow: /about-me\n"
            "Disallow: /notes\n"
            "Disallow: /competency-matrix\n"
            "Disallow: /sitemap\n"
            "Sitemap: http://localhost:8000/sitemap.xml\n"
        )
