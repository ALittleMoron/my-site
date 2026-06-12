import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiClient, QueryParams } from '../../../core/http/api-client.service';
import { LanguageCode } from '../../../core/i18n/i18n.model';
import {
  AdminMatrixQuestionDetailDto,
  AdminMatrixQuestionPayload,
  AdminMatrixQuestionWorkspace,
  AdminMatrixQuestionWorkspaceFilters,
  AdminMatrixResource,
  AdminMatrixResourcesDto,
  AdminMatrixWorkspaceDto,
  AdminMatrixWorkspaceFilterOptions,
  AdminMatrixWorkspaceFilterOptionsDto,
  MatrixItemsListDto,
  MatrixSheetsDto,
  mapPublicQuestionsDto,
  mapPublicSheetsDto,
  AdminReadonlyMatrixQuestionList,
  AdminReadonlyMatrixSheet,
} from '../models/matrix-question-workspace.model';

@Injectable({ providedIn: 'root' })
export class MatrixQuestionWorkspaceService {
  private readonly api = inject(ApiClient);

  listWorkspaceItems(
    filters: AdminMatrixQuestionWorkspaceFilters,
  ): Observable<AdminMatrixQuestionWorkspace> {
    return this.api
      .get<AdminMatrixWorkspaceDto>(
        '/api/admin/competency-matrix/items/workspace',
        workspaceQueryParams(filters),
      )
      .pipe(map((dto) => dto));
  }

  getFilterOptions(language: LanguageCode): Observable<AdminMatrixWorkspaceFilterOptions> {
    return this.api
      .get<AdminMatrixWorkspaceFilterOptionsDto>(
        '/api/admin/competency-matrix/items/filter-options',
        { language },
      )
      .pipe(map((dto) => dto));
  }

  listPublicPreviewSheets(language: LanguageCode): Observable<AdminReadonlyMatrixSheet[]> {
    return this.api
      .get<MatrixSheetsDto>('/api/competency-matrix/sheets', { language })
      .pipe(map(mapPublicSheetsDto));
  }

  listPublicPreviewQuestions(
    sheetKey: string,
    language: LanguageCode,
  ): Observable<AdminReadonlyMatrixQuestionList> {
    return this.api
      .get<MatrixItemsListDto>('/api/competency-matrix/items', { sheetKey, language })
      .pipe(map(mapPublicQuestionsDto));
  }

  getQuestion(id: number, language: LanguageCode): Observable<AdminMatrixQuestionDetailDto> {
    return this.api.get<AdminMatrixQuestionDetailDto>(
      `/api/admin/competency-matrix/items/detail/${id}`,
      {
        onlyPublished: 'false',
        language,
      },
    );
  }

  createQuestion(
    payload: AdminMatrixQuestionPayload,
    language: LanguageCode,
  ): Observable<AdminMatrixQuestionDetailDto> {
    return this.api.post<AdminMatrixQuestionDetailDto>(
      '/api/admin/competency-matrix/items',
      payload,
      { language },
    );
  }

  updateQuestion(
    id: number,
    payload: AdminMatrixQuestionPayload,
    language: LanguageCode,
  ): Observable<AdminMatrixQuestionDetailDto> {
    return this.api.put<AdminMatrixQuestionDetailDto>(
      `/api/admin/competency-matrix/items/detail/${id}`,
      payload,
      { language },
    );
  }

  publishQuestion(id: number): Observable<void> {
    return this.api.post<void>(`/api/admin/competency-matrix/items/detail/${id}/set-published`, {});
  }

  unpublishQuestion(id: number): Observable<void> {
    return this.api.post<void>(`/api/admin/competency-matrix/items/detail/${id}/set-draft`, {});
  }

  deleteQuestion(id: number): Observable<void> {
    return this.api.delete<void>(`/api/admin/competency-matrix/items/detail/${id}`);
  }

  searchResources(
    searchName: string,
    limit: number,
    language: LanguageCode,
  ): Observable<AdminMatrixResource[]> {
    return this.api
      .get<AdminMatrixResourcesDto>('/api/admin/competency-matrix/resources/search', {
        searchName,
        limit: String(limit),
        language,
      })
      .pipe(map((dto) => dto.resources));
  }
}

function workspaceQueryParams(filters: AdminMatrixQuestionWorkspaceFilters): QueryParams {
  const params: Record<string, string | readonly string[]> = {
    page: String(filters.page),
    pageSize: String(filters.pageSize),
    language: filters.language,
    sort: filters.sort,
  };
  setOptionalString(params, 'searchQuery', filters.searchQuery);
  setOptionalArray(params, 'sheetKeys', filters.sheetKeys);
  setOptionalArray(params, 'grades', filters.grades);
  setOptionalArray(params, 'sections', filters.sections);
  setOptionalArray(params, 'subsections', filters.subsections);
  setOptionalArray(params, 'publishStatuses', filters.publishStatuses);
  setOptionalString(params, 'publishedFrom', filters.publishedFrom);
  setOptionalString(params, 'publishedTo', filters.publishedTo);
  if (filters.hasMissingFields !== undefined) {
    params['hasMissingFields'] = String(filters.hasMissingFields);
  }
  return params;
}

function setOptionalString(
  params: Record<string, string | readonly string[]>,
  key: string,
  value: string | undefined,
): void {
  const normalized = value?.trim();
  if (normalized) {
    params[key] = normalized;
  }
}

function setOptionalArray(
  params: Record<string, string | readonly string[]>,
  key: string,
  value: readonly string[] | undefined,
): void {
  if (value !== undefined && value.length > 0) {
    params[key] = value;
  }
}
