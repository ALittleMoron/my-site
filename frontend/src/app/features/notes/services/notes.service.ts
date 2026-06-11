import { Injectable, inject } from '@angular/core';
import { Observable, map, of, switchMap } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import { LanguageCode } from '../../../core/i18n/i18n.model';
import {
  NoteDetail,
  NoteDetailDto,
  NoteList,
  NoteListDto,
  NoteListParams,
  NotePayload,
  NotePublicStats,
  NotePublicStatsCollectionDto,
  NoteReactionPayload,
  NoteStats,
  NoteStatsDto,
  NoteStatsParams,
  NoteTag,
  NoteTagDto,
  NoteTree,
  NoteTreeDto,
  TagPayload,
  TagsDto,
  mapNoteDetailDto,
  mapNoteListDto,
  mapNoteStatsDto,
  mapNoteTreeDto,
  mapPublicStatsCollectionDto,
  mapTagDto,
} from '../models/notes.model';

type PublicNoteListParams = Omit<NoteListParams, 'onlyPublished'>;

@Injectable({ providedIn: 'root' })
export class NotesService {
  private readonly api = inject(ApiClient);

  getPublicNotes(params: PublicNoteListParams): Observable<NoteList> {
    const queryParams: Record<string, string | readonly string[]> = {
      page: String(params.page),
      pageSize: String(params.pageSize),
      language: params.language,
    };
    this.applyOptionalListParams(queryParams, params);
    return this.getNotesFromPath('/api/notes', queryParams);
  }

  getAdminNotes(params: NoteListParams): Observable<NoteList> {
    const queryParams: Record<string, string | readonly string[]> = {
      page: String(params.page),
      pageSize: String(params.pageSize),
      language: params.language,
      onlyPublished: String(params.onlyPublished),
    };
    this.applyOptionalListParams(queryParams, params);
    return this.getNotesFromPath('/api/admin/notes', queryParams);
  }

  private applyOptionalListParams(
    queryParams: Record<string, string | readonly string[]>,
    params: PublicNoteListParams,
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

  private getNotesFromPath(
    path: string,
    queryParams: Record<string, string | readonly string[]>,
  ): Observable<NoteList> {
    return this.api.get<NoteListDto>(path, queryParams).pipe(
      switchMap((dto) => {
        const noteIds = dto.notes.map((note) => note.id);
        if (noteIds.length === 0) {
          return of(mapNoteListDto(dto, new Map<string, NotePublicStats>()));
        }
        return this.getPublicStats(noteIds).pipe(
          map((statsByNoteId) => mapNoteListDto(dto, statsByNoteId)),
        );
      }),
    );
  }

  getPublicNote(slug: string, language: LanguageCode): Observable<NoteDetail> {
    return this.api
      .get<NoteDetailDto>(`/api/notes/detail/${slug}`, { language })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  getAdminNote(
    slug: string,
    onlyPublished: boolean,
    language: LanguageCode,
  ): Observable<NoteDetail> {
    return this.api
      .get<NoteDetailDto>(`/api/admin/notes/detail/${slug}`, {
        language,
        onlyPublished: String(onlyPublished),
      })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  trackPublicView(slug: string, language: LanguageCode): Observable<void> {
    return this.api.post<void>(`/api/notes/detail/${slug}/analytics/view`, {}, { language });
  }

  trackPublicEngagedView(slug: string, language: LanguageCode): Observable<void> {
    return this.api.post<void>(
      `/api/notes/detail/${slug}/analytics/engaged-view`,
      {},
      { language },
    );
  }

  setPublicReaction(
    slug: string,
    payload: NoteReactionPayload,
    language: LanguageCode,
  ): Observable<void> {
    return this.api.post<void>(`/api/notes/detail/${slug}/reaction`, payload, { language });
  }

  getAdminStats(params: NoteStatsParams): Observable<NoteStats> {
    return this.api
      .get<NoteStatsDto>('/api/admin/notes/stats', {
        dateFrom: params.dateFrom,
        dateTo: params.dateTo,
        language: params.language,
      })
      .pipe(map(mapNoteStatsDto));
  }

  getPublicTree(language: LanguageCode): Observable<NoteTree> {
    return this.api.get<NoteTreeDto>('/api/notes/tree', { language }).pipe(map(mapNoteTreeDto));
  }

  getAdminTree(language: LanguageCode): Observable<NoteTree> {
    return this.api
      .get<NoteTreeDto>('/api/admin/notes/tree', { language })
      .pipe(map(mapNoteTreeDto));
  }

  createAdminNote(payload: NotePayload, language: LanguageCode): Observable<NoteDetail> {
    return this.api
      .post<NoteDetailDto>('/api/admin/notes', payload, { language })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  updateAdminNote(
    slug: string,
    payload: NotePayload,
    language: LanguageCode,
  ): Observable<NoteDetail> {
    return this.api
      .put<NoteDetailDto>(`/api/admin/notes/detail/${slug}`, payload, { language })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  deleteAdminNote(slug: string): Observable<void> {
    return this.api.delete<void>(`/api/admin/notes/detail/${slug}`);
  }

  publishAdminNote(slug: string): Observable<void> {
    return this.api.post<void>(`/api/admin/notes/detail/${slug}/set-published`, {});
  }

  unpublishAdminNote(slug: string): Observable<void> {
    return this.api.post<void>(`/api/admin/notes/detail/${slug}/set-draft`, {});
  }

  getPublicTags(language: LanguageCode): Observable<NoteTag[]> {
    return this.api
      .get<TagsDto>('/api/notes/tags', { language })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  getAdminTags(includeDeleted: boolean, language: LanguageCode): Observable<NoteTag[]> {
    return this.api
      .get<TagsDto>('/api/admin/notes/tags', { includeDeleted: String(includeDeleted), language })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  searchAdminTags(
    searchName: string,
    includeDeleted: boolean,
    limit: number,
    language: LanguageCode,
  ): Observable<NoteTag[]> {
    return this.api
      .get<TagsDto>('/api/admin/notes/tags/search', {
        searchName,
        includeDeleted: String(includeDeleted),
        limit: String(limit),
        language,
      })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  createAdminTag(payload: TagPayload, language: LanguageCode): Observable<NoteTag> {
    return this.api
      .post<NoteTagDto>('/api/admin/notes/tags', payload, { language })
      .pipe(map(mapTagDto));
  }

  updateAdminTag(tagId: number, payload: TagPayload, language: LanguageCode): Observable<NoteTag> {
    return this.api
      .put<NoteTagDto>(`/api/admin/notes/tags/${tagId}`, payload, { language })
      .pipe(map(mapTagDto));
  }

  deleteAdminTag(tagId: number): Observable<void> {
    return this.api.delete<void>(`/api/admin/notes/tags/${tagId}`);
  }

  restoreAdminTag(tagId: number): Observable<void> {
    return this.api.post<void>(`/api/admin/notes/tags/${tagId}/restore`, {});
  }

  private mapDetailWithPublicStats(dto: NoteDetailDto): Observable<NoteDetail> {
    return this.getPublicStats([dto.id]).pipe(
      map((statsByNoteId) => mapNoteDetailDto(dto, statsByNoteId)),
    );
  }

  private getPublicStats(
    noteIds: readonly string[],
  ): Observable<ReadonlyMap<string, NotePublicStats>> {
    return this.api
      .get<NotePublicStatsCollectionDto>('/api/notes/public-stats', { noteIds })
      .pipe(map(mapPublicStatsCollectionDto));
  }
}
