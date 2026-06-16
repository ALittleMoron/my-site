import { Injectable, inject } from '@angular/core';
import { Observable, map, of, switchMap } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import { LanguageCode } from '../../../core/i18n/i18n.model';
import {
  ArticleDetail,
  ArticleDetailDto,
  ArticleList,
  ArticleListDto,
  ArticleListParams,
  ArticlePayload,
  ArticlePublicStats,
  ArticlePublicStatsCollectionDto,
  ArticleReactionPayload,
  ArticleStats,
  ArticleStatsDto,
  ArticleStatsParams,
  ArticleTag,
  ArticleTagDto,
  ArticleTree,
  ArticleTreeDto,
  TagPayload,
  TagsDto,
  mapArticleDetailDto,
  mapArticleListDto,
  mapArticleStatsDto,
  mapArticleTreeDto,
  mapPublicStatsCollectionDto,
  mapTagDto,
} from '../models/articles.model';

type PublicArticleListParams = Omit<ArticleListParams, 'onlyPublished'>;

@Injectable({ providedIn: 'root' })
export class ArticlesService {
  private readonly api = inject(ApiClient);

  getPublicArticles(params: PublicArticleListParams): Observable<ArticleList> {
    const queryParams: Record<string, string | readonly string[]> = {
      page: String(params.page),
      pageSize: String(params.pageSize),
      language: params.language,
    };
    this.applyOptionalListParams(queryParams, params);
    return this.getArticlesFromPath('/api/articles', queryParams);
  }

  getAdminArticles(params: ArticleListParams): Observable<ArticleList> {
    const queryParams: Record<string, string | readonly string[]> = {
      page: String(params.page),
      pageSize: String(params.pageSize),
      language: params.language,
      onlyPublished: String(params.onlyPublished),
    };
    this.applyOptionalListParams(queryParams, params);
    return this.getArticlesFromPath('/api/admin/articles', queryParams);
  }

  private applyOptionalListParams(
    queryParams: Record<string, string | readonly string[]>,
    params: PublicArticleListParams,
  ): void {
    if (params.tagSlug) {
      queryParams['tagSlug'] = params.tagSlug;
    }
    if (params.publishedFrom) {
      queryParams['publishedFrom'] = params.publishedFrom;
    }
    if (params.publishedTo) {
      queryParams['publishedTo'] = params.publishedTo;
    }
    if (params.searchQuery) {
      queryParams['searchQuery'] = params.searchQuery;
    }
  }

  private getArticlesFromPath(
    path: string,
    queryParams: Record<string, string | readonly string[]>,
  ): Observable<ArticleList> {
    return this.api.get<ArticleListDto>(path, queryParams).pipe(
      switchMap((dto) => {
        const articleIds = dto.articles.map((article) => article.id);
        if (articleIds.length === 0) {
          return of(mapArticleListDto(dto, new Map<string, ArticlePublicStats>()));
        }
        return this.getPublicStats(articleIds).pipe(
          map((statsByArticleId) => mapArticleListDto(dto, statsByArticleId)),
        );
      }),
    );
  }

  getPublicArticle(slug: string, language: LanguageCode): Observable<ArticleDetail> {
    return this.api
      .get<ArticleDetailDto>(`/api/articles/detail/${slug}`, { language })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  getAdminArticle(
    slug: string,
    onlyPublished: boolean,
    language: LanguageCode,
  ): Observable<ArticleDetail> {
    return this.api
      .get<ArticleDetailDto>(`/api/admin/articles/detail/${slug}`, {
        language,
        onlyPublished: String(onlyPublished),
      })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  trackPublicView(slug: string, language: LanguageCode): Observable<void> {
    return this.api.post<void>(`/api/articles/detail/${slug}/analytics/view`, {}, { language });
  }

  trackPublicEngagedView(slug: string, language: LanguageCode): Observable<void> {
    return this.api.post<void>(
      `/api/articles/detail/${slug}/analytics/engaged-view`,
      {},
      { language },
    );
  }

  setPublicReaction(
    slug: string,
    payload: ArticleReactionPayload,
    language: LanguageCode,
  ): Observable<void> {
    return this.api.post<void>(`/api/articles/detail/${slug}/reaction`, payload, { language });
  }

  getAdminStats(params: ArticleStatsParams): Observable<ArticleStats> {
    return this.api
      .get<ArticleStatsDto>('/api/admin/articles/stats', {
        dateFrom: params.dateFrom,
        dateTo: params.dateTo,
        language: params.language,
      })
      .pipe(map(mapArticleStatsDto));
  }

  getPublicTree(language: LanguageCode): Observable<ArticleTree> {
    return this.api
      .get<ArticleTreeDto>('/api/articles/tree', { language })
      .pipe(map(mapArticleTreeDto));
  }

  getAdminTree(language: LanguageCode): Observable<ArticleTree> {
    return this.api
      .get<ArticleTreeDto>('/api/admin/articles/tree', { language })
      .pipe(map(mapArticleTreeDto));
  }

  createAdminArticle(payload: ArticlePayload, language: LanguageCode): Observable<ArticleDetail> {
    return this.api
      .post<ArticleDetailDto>('/api/admin/articles', payload, { language })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  updateAdminArticle(
    slug: string,
    payload: ArticlePayload,
    language: LanguageCode,
  ): Observable<ArticleDetail> {
    return this.api
      .put<ArticleDetailDto>(`/api/admin/articles/detail/${slug}`, payload, { language })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  deleteAdminArticle(slug: string): Observable<void> {
    return this.api.delete<void>(`/api/admin/articles/detail/${slug}`);
  }

  publishAdminArticle(slug: string): Observable<void> {
    return this.api.post<void>(`/api/admin/articles/detail/${slug}/set-published`, {});
  }

  unpublishAdminArticle(slug: string): Observable<void> {
    return this.api.post<void>(`/api/admin/articles/detail/${slug}/set-draft`, {});
  }

  getPublicTags(language: LanguageCode): Observable<ArticleTag[]> {
    return this.api
      .get<TagsDto>('/api/articles/tags', { language })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  getAdminTags(includeDeleted: boolean, language: LanguageCode): Observable<ArticleTag[]> {
    return this.api
      .get<TagsDto>('/api/admin/articles/tags', {
        includeDeleted: String(includeDeleted),
        language,
      })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  searchAdminTags(
    searchName: string,
    includeDeleted: boolean,
    limit: number,
    language: LanguageCode,
  ): Observable<ArticleTag[]> {
    return this.api
      .get<TagsDto>('/api/admin/articles/tags/search', {
        searchName,
        includeDeleted: String(includeDeleted),
        limit: String(limit),
        language,
      })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  createAdminTag(payload: TagPayload, language: LanguageCode): Observable<ArticleTag> {
    return this.api
      .post<ArticleTagDto>('/api/admin/articles/tags', payload, { language })
      .pipe(map(mapTagDto));
  }

  updateAdminTag(
    tagId: number,
    payload: TagPayload,
    language: LanguageCode,
  ): Observable<ArticleTag> {
    return this.api
      .put<ArticleTagDto>(`/api/admin/articles/tags/${tagId}`, payload, { language })
      .pipe(map(mapTagDto));
  }

  deleteAdminTag(tagId: number): Observable<void> {
    return this.api.delete<void>(`/api/admin/articles/tags/${tagId}`);
  }

  restoreAdminTag(tagId: number): Observable<void> {
    return this.api.post<void>(`/api/admin/articles/tags/${tagId}/restore`, {});
  }

  private mapDetailWithPublicStats(dto: ArticleDetailDto): Observable<ArticleDetail> {
    return this.getPublicStats([dto.id]).pipe(
      map((statsByArticleId) => mapArticleDetailDto(dto, statsByArticleId)),
    );
  }

  private getPublicStats(
    articleIds: readonly string[],
  ): Observable<ReadonlyMap<string, ArticlePublicStats>> {
    return this.api
      .get<ArticlePublicStatsCollectionDto>('/api/articles/public-stats', { articleIds })
      .pipe(map(mapPublicStatsCollectionDto));
  }
}
