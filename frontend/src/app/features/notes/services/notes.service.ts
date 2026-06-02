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

@Injectable({ providedIn: 'root' })
export class NotesService {
  private readonly api = inject(ApiClient);

  getNotes(params: NoteListParams): Observable<NoteList> {
    const queryParams: Record<string, string | readonly string[]> = {
      page: String(params.page),
      pageSize: String(params.pageSize),
      language: params.language,
      onlyPublished: String(params.onlyPublished),
    };
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
    return this.api.get<NoteListDto>('/api/notes', queryParams).pipe(
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

  getNote(slug: string, onlyPublished: boolean, language: LanguageCode): Observable<NoteDetail> {
    return this.api
      .get<NoteDetailDto>(`/api/notes/detail/${slug}`, {
        language,
        onlyPublished: String(onlyPublished),
      })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  trackView(slug: string, language: LanguageCode): Observable<void> {
    return this.api.post<void>(`/api/notes/detail/${slug}/analytics/view`, {}, { language });
  }

  trackEngagedView(slug: string, language: LanguageCode): Observable<void> {
    return this.api.post<void>(
      `/api/notes/detail/${slug}/analytics/engaged-view`,
      {},
      { language },
    );
  }

  setReaction(
    slug: string,
    payload: NoteReactionPayload,
    language: LanguageCode,
  ): Observable<void> {
    return this.api.post<void>(`/api/notes/detail/${slug}/reaction`, payload, { language });
  }

  getStats(params: NoteStatsParams): Observable<NoteStats> {
    return this.api
      .get<NoteStatsDto>('/api/notes/stats', {
        dateFrom: params.dateFrom,
        dateTo: params.dateTo,
        language: params.language,
      })
      .pipe(map(mapNoteStatsDto));
  }

  getTree(language: LanguageCode): Observable<NoteTree> {
    return this.api.get<NoteTreeDto>('/api/notes/tree', { language }).pipe(map(mapNoteTreeDto));
  }

  createNote(payload: NotePayload, language: LanguageCode): Observable<NoteDetail> {
    return this.api
      .post<NoteDetailDto>('/api/notes', payload, { language })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  updateNote(slug: string, payload: NotePayload, language: LanguageCode): Observable<NoteDetail> {
    return this.api
      .put<NoteDetailDto>(`/api/notes/detail/${slug}`, payload, { language })
      .pipe(switchMap((dto) => this.mapDetailWithPublicStats(dto)));
  }

  deleteNote(slug: string): Observable<void> {
    return this.api.delete<void>(`/api/notes/detail/${slug}`);
  }

  publishNote(slug: string): Observable<void> {
    return this.api.post<void>(`/api/notes/detail/${slug}/set-published`, {});
  }

  unpublishNote(slug: string): Observable<void> {
    return this.api.post<void>(`/api/notes/detail/${slug}/set-draft`, {});
  }

  getTags(includeDeleted: boolean, language: LanguageCode): Observable<NoteTag[]> {
    return this.api
      .get<TagsDto>('/api/notes/tags', { includeDeleted: String(includeDeleted), language })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  searchTags(
    searchName: string,
    includeDeleted: boolean,
    limit: number,
    language: LanguageCode,
  ): Observable<NoteTag[]> {
    return this.api
      .get<TagsDto>('/api/notes/tags/search', {
        searchName,
        includeDeleted: String(includeDeleted),
        limit: String(limit),
        language,
      })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  createTag(payload: TagPayload, language: LanguageCode): Observable<NoteTag> {
    return this.api.post<NoteTagDto>('/api/notes/tags', payload, { language }).pipe(map(mapTagDto));
  }

  updateTag(tagId: number, payload: TagPayload, language: LanguageCode): Observable<NoteTag> {
    return this.api
      .put<NoteTagDto>(`/api/notes/tags/${tagId}`, payload, { language })
      .pipe(map(mapTagDto));
  }

  deleteTag(tagId: number): Observable<void> {
    return this.api.delete<void>(`/api/notes/tags/${tagId}`);
  }

  restoreTag(tagId: number): Observable<void> {
    return this.api.post<void>(`/api/notes/tags/${tagId}/restore`, {});
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
