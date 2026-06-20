import hmac
from dataclasses import dataclass
from datetime import UTC, date, datetime
from hashlib import sha256
from urllib.parse import urlparse
from uuid import UUID

from core.articles.enums import ArticleReactionKind, ArticleViewSourceCategory
from core.articles.event_dispatchers import ArticleAnalyticsErrorReporter
from core.articles.exceptions import ArticleNotFoundError, TagNotFoundError
from core.articles.schemas import (
    Article,
    ArticleAnalyticsStats,
    ArticleCreateParams,
    ArticleFilters,
    ArticlePublicStatsCollection,
    Articles,
    ArticleTree,
    ArticleUpdateParams,
    PublishedArticlesForSeo,
    Tag,
    TagCreateParams,
    Tags,
    TagUpdateParams,
)
from core.articles.storages import ArticleAnalyticsStorage, ArticlesStorage
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from core.schemas import Secret
from core.types import IntId


@dataclass(kw_only=True, slots=True, frozen=True)
class ArticlesUseCase:
    storage: ArticlesStorage

    async def get_article(self, *, slug: str, only_published: bool) -> Article:
        article = await self.storage.get_article_by_slug(
            slug=slug,
            include_deleted_tags=not only_published,
        )
        if only_published and not article.is_available():
            raise ArticleNotFoundError
        return article.public_copy() if only_published else article

    async def list_articles(self, *, filters: ArticleFilters) -> Articles:
        if filters.page is None or filters.page_size is None:
            message = "pagination required"
            raise ValueError(message)
        articles, total_count = await self.storage.list_articles(filters=filters)
        return Articles.from_page(
            values=articles,
            total_count=total_count,
            page_size=filters.page_size,
        )

    async def list_published_articles_for_seo(self) -> PublishedArticlesForSeo:
        articles, _total_count = await self.storage.list_articles(
            filters=ArticleFilters(only_published=True, include_tags=False, order_for_seo=True),
        )
        available_articles = [article for article in articles if article.is_available()]
        return PublishedArticlesForSeo.from_articles(articles=available_articles)

    async def list_tree(self, *, only_published: bool, language: LanguageEnum) -> ArticleTree:
        items = await self.storage.list_tree_items(
            only_published=only_published,
            language=language,
        )
        return ArticleTree.from_items(items=items)

    async def create_article(self, *, params: ArticleCreateParams) -> Article:
        tags = await self._get_active_tags(tag_ids=params.tag_ids)
        now = datetime.now(tz=UTC)
        return await self.storage.create_article(article=params.to_article(now=now, tags=tags))

    async def update_article(
        self,
        *,
        slug: str,
        params: ArticleUpdateParams,
    ) -> Article:
        existing_article = await self.storage.get_article_by_slug(
            slug=slug,
            include_deleted_tags=True,
        )
        tags = await self._get_active_tags(tag_ids=params.tag_ids)
        now = datetime.now(tz=UTC)
        return await self.storage.update_article(
            article=params.to_article(existing_article=existing_article, now=now, tags=tags),
        )

    async def _get_active_tags(self, *, tag_ids: list[IntId]) -> Tags:
        tags = await self.storage.get_tags_by_ids(
            tag_ids=tag_ids,
            include_deleted=False,
        )
        if not tags.all_tags_exist_by_ids(ids=set(tag_ids)):
            raise TagNotFoundError
        return tags

    async def delete_article(self, *, slug: str) -> None:
        await self.storage.delete_article(slug=slug)

    async def switch_article_publish_status(
        self,
        *,
        slug: str,
        publish_status: PublishStatusEnum,
    ) -> None:
        await self.storage.update_article_publish_status(slug=slug, publish_status=publish_status)

    async def list_tags(self, *, include_deleted: bool, language: LanguageEnum) -> Tags:
        return await self.storage.list_tags(include_deleted=include_deleted, language=language)

    async def search_tags(
        self,
        *,
        search_name: str,
        include_deleted: bool,
        limit: int,
        language: LanguageEnum,
    ) -> Tags:
        return await self.storage.search_tags(
            search_name=search_name,
            include_deleted=include_deleted,
            limit=limit,
            language=language,
        )

    async def create_tag(self, *, params: TagCreateParams) -> Tag:
        return await self.storage.create_tag(tag=params.to_tag())

    async def update_tag(
        self,
        *,
        tag_id: IntId,
        params: TagUpdateParams,
    ) -> Tag:
        return await self.storage.update_tag(tag=params.to_tag(tag_id=tag_id))

    async def soft_delete_tag(self, *, tag_id: IntId) -> None:
        await self.storage.soft_delete_tag(tag_id=tag_id)

    async def restore_tag(self, *, tag_id: IntId) -> None:
        await self.storage.restore_tag(tag_id=tag_id)


@dataclass(kw_only=True, slots=True, frozen=True)
class ArticleAnalyticsUseCase:
    articles_storage: ArticlesStorage
    analytics_storage: ArticleAnalyticsStorage
    reaction_secret: Secret[str]
    app_domain: str
    error_reporter: ArticleAnalyticsErrorReporter

    async def track_public_view(
        self,
        *,
        article: Article,
        referrer: str | None,
    ) -> None:
        try:
            await self.track_view(
                article=article,
                source_category=self._classify_source_category(referrer=referrer),
            )
        except Exception as exc:  # noqa: BLE001
            self.error_reporter.report_public_view_tracking_failure(article=article, error=exc)

    async def track_view(
        self,
        *,
        article: Article,
        source_category: ArticleViewSourceCategory,
    ) -> None:
        if not article.is_available():
            return
        await self.analytics_storage.increment_view(
            article_id=article.id,
            source_category=source_category,
            viewed_on=None,
        )

    async def track_engaged_view(
        self,
        *,
        slug: str,
        source_category: ArticleViewSourceCategory,
    ) -> None:
        article = await self._get_published_article(slug=slug)
        await self.analytics_storage.increment_engaged_view(
            article_id=article.id,
            source_category=source_category,
            viewed_on=None,
        )

    async def get_public_stats(self, *, article_ids: list[UUID]) -> ArticlePublicStatsCollection:
        unique_article_ids = list(dict.fromkeys(article_ids))
        stats = await self.analytics_storage.get_public_stats(article_ids=unique_article_ids)
        return stats.fill_missing(article_ids=unique_article_ids)

    async def set_reaction(
        self,
        *,
        slug: str,
        client_token: str,
        reaction_kind: ArticleReactionKind | None,
    ) -> None:
        article = await self._get_published_article(slug=slug)
        await self.analytics_storage.set_reaction(
            article_id=article.id,
            article_scoped_voter_hash=self._build_article_scoped_voter_hash(
                article_id=article.id,
                client_token=client_token,
            ),
            reaction_kind=reaction_kind,
        )

    async def get_stats(
        self,
        *,
        date_from: date,
        date_to: date,
        language: LanguageEnum,
    ) -> ArticleAnalyticsStats:
        daily = await self.analytics_storage.get_daily_stats(
            date_from=date_from,
            date_to=date_to,
            language=language,
        )
        article_ids = list(dict.fromkeys(item.article_id for item in daily))
        reaction_counts = await self.analytics_storage.get_reaction_counts(article_ids=article_ids)
        return ArticleAnalyticsStats.from_daily_stats(
            date_from=date_from,
            date_to=date_to,
            daily=daily,
            reaction_counts=reaction_counts,
        )

    async def _get_published_article(self, *, slug: str) -> Article:
        article = await self.articles_storage.get_article_by_slug(
            slug=slug,
            include_deleted_tags=False,
        )
        if not article.is_available():
            raise ArticleNotFoundError
        return article

    def _classify_source_category(self, *, referrer: str | None) -> ArticleViewSourceCategory:
        if not referrer:
            return ArticleViewSourceCategory.DIRECT
        hostname = urlparse(referrer).hostname
        if hostname is None:
            return ArticleViewSourceCategory.UNKNOWN
        normalized_hostname = hostname.lower()
        app_domain = self.app_domain.lower()
        if normalized_hostname == app_domain or normalized_hostname.endswith(f".{app_domain}"):
            return ArticleViewSourceCategory.INTERNAL
        if self._is_search_hostname(hostname=normalized_hostname):
            return ArticleViewSourceCategory.SEARCH
        if self._is_social_hostname(hostname=normalized_hostname):
            return ArticleViewSourceCategory.SOCIAL
        return ArticleViewSourceCategory.EXTERNAL

    def _is_search_hostname(self, *, hostname: str) -> bool:
        return any(
            search_hostname in hostname
            for search_hostname in (
                "google.",
                "yandex.",
                "bing.",
                "duckduckgo.",
                "search.yahoo.",
            )
        )

    def _is_social_hostname(self, *, hostname: str) -> bool:
        return any(
            social_hostname in hostname
            for social_hostname in (
                "facebook.",
                "linkedin.",
                "reddit.",
                "t.me",
                "telegram.",
                "twitter.",
                "x.com",
                "vk.",
            )
        )

    def _build_article_scoped_voter_hash(self, *, article_id: UUID, client_token: str) -> str:
        message = f"{article_id}:{client_token}".encode()
        return hmac.new(
            self.reaction_secret.get_secret_value().encode(),
            message,
            sha256,
        ).hexdigest()
