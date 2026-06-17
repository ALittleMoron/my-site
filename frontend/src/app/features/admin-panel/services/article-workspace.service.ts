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
  ArticleTag,
  ArticleTagDto,
  ArticleTree,
  ArticleTreeDto,
  TagPayload,
  TagsDto,
  mapArticleDetailDto,
  mapArticleListDto,
  mapArticleTreeDto,
  mapPublicStatsCollectionDto,
  mapTagDto,
} from '../models/article-workspace.model';

@Injectable({ providedIn: 'root' })
export class ArticleWorkspaceService {
  private readonly api = inject(ApiClient);

  listArticles(params: ArticleListParams): Observable<ArticleList> {
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
    params: ArticleListParams,
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

  getArticle(slug: string, language: LanguageCode): Observable<ArticleDetail> {
    return this.api
      .get<ArticleDetailDto>(`/api/admin/articles/detail/${slug}`, {
        language,
        onlyPublished: 'false',
      })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  getTree(language: LanguageCode): Observable<ArticleTree> {
    return this.api
      .get<ArticleTreeDto>('/api/admin/articles/tree', { language })
      .pipe(map(mapArticleTreeDto));
  }

  createArticle(payload: ArticlePayload, language: LanguageCode): Observable<ArticleDetail> {
    return this.api
      .post<ArticleDetailDto>('/api/admin/articles', payload, { language })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  updateArticle(
    slug: string,
    payload: ArticlePayload,
    language: LanguageCode,
  ): Observable<ArticleDetail> {
    return this.api
      .put<ArticleDetailDto>(`/api/admin/articles/detail/${slug}`, payload, { language })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  deleteArticle(slug: string): Observable<void> {
    return this.api.delete<void>(`/api/admin/articles/detail/${slug}`);
  }

  publishArticle(slug: string): Observable<void> {
    return this.api.post<void>(`/api/admin/articles/detail/${slug}/set-published`, {});
  }

  unpublishArticle(slug: string): Observable<void> {
    return this.api.post<void>(`/api/admin/articles/detail/${slug}/set-draft`, {});
  }

  getTags(includeDeleted: boolean, language: LanguageCode): Observable<ArticleTag[]> {
    return this.api
      .get<TagsDto>('/api/admin/articles/tags', {
        includeDeleted: String(includeDeleted),
        language,
      })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  searchTags(
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

  createTag(payload: TagPayload, language: LanguageCode): Observable<ArticleTag> {
    return this.api
      .post<ArticleTagDto>('/api/admin/articles/tags', payload, { language })
      .pipe(map(mapTagDto));
  }

  updateTag(tagId: number, payload: TagPayload, language: LanguageCode): Observable<ArticleTag> {
    return this.api
      .put<ArticleTagDto>(`/api/admin/articles/tags/${tagId}`, payload, { language })
      .pipe(map(mapTagDto));
  }

  deleteTag(tagId: number): Observable<void> {
    return this.api.delete<void>(`/api/admin/articles/tags/${tagId}`);
  }

  restoreTag(tagId: number): Observable<void> {
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
