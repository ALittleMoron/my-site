import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import {
  NoteDetail,
  NoteDetailDto,
  NoteList,
  NoteListDto,
  NoteListParams,
  NotePayload,
  NoteTag,
  NoteTagDto,
  NoteTree,
  NoteTreeDto,
  TagPayload,
  TagsDto,
  mapNoteDetailDto,
  mapNoteListDto,
  mapNoteTreeDto,
  mapTagDto,
} from '../models/notes.model';

@Injectable({ providedIn: 'root' })
export class NotesService {
  private readonly api = inject(ApiClient);

  getNotes(params: NoteListParams): Observable<NoteList> {
    const queryParams: Record<string, string> = {
      page: String(params.page),
      pageSize: String(params.pageSize),
      onlyPublished: String(params.onlyPublished),
    };
    if (params.tagSlug) {
      queryParams['tagSlug'] = params.tagSlug;
    }
    return this.api.get<NoteListDto>('/api/notes', queryParams).pipe(map(mapNoteListDto));
  }

  getNote(slug: string, onlyPublished: boolean): Observable<NoteDetail> {
    return this.api
      .get<NoteDetailDto>(`/api/notes/detail/${slug}`, {
        onlyPublished: String(onlyPublished),
      })
      .pipe(map(mapNoteDetailDto));
  }

  getTree(): Observable<NoteTree> {
    return this.api.get<NoteTreeDto>('/api/notes/tree').pipe(map(mapNoteTreeDto));
  }

  createNote(payload: NotePayload): Observable<NoteDetail> {
    return this.api.post<NoteDetailDto>('/api/notes', payload).pipe(map(mapNoteDetailDto));
  }

  updateNote(slug: string, payload: NotePayload): Observable<NoteDetail> {
    return this.api
      .put<NoteDetailDto>(`/api/notes/detail/${slug}`, payload)
      .pipe(map(mapNoteDetailDto));
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

  getTags(includeDeleted: boolean): Observable<NoteTag[]> {
    return this.api
      .get<TagsDto>('/api/notes/tags', { includeDeleted: String(includeDeleted) })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  searchTags(searchName: string, includeDeleted: boolean, limit: number): Observable<NoteTag[]> {
    return this.api
      .get<TagsDto>('/api/notes/tags/search', {
        searchName,
        includeDeleted: String(includeDeleted),
        limit: String(limit),
      })
      .pipe(map((dto) => dto.tags.map(mapTagDto)));
  }

  createTag(payload: TagPayload): Observable<NoteTag> {
    return this.api.post<NoteTagDto>('/api/notes/tags', payload).pipe(map(mapTagDto));
  }

  updateTag(tagId: number, payload: TagPayload): Observable<NoteTag> {
    return this.api.put<NoteTagDto>(`/api/notes/tags/${tagId}`, payload).pipe(map(mapTagDto));
  }

  deleteTag(tagId: number): Observable<void> {
    return this.api.delete<void>(`/api/notes/tags/${tagId}`);
  }

  restoreTag(tagId: number): Observable<void> {
    return this.api.post<void>(`/api/notes/tags/${tagId}/restore`, {});
  }
}
