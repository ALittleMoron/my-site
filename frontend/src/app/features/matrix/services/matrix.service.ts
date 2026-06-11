import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import { LanguageCode } from '../../../core/i18n/i18n.model';
import {
  MatrixItemDetailDto,
  MatrixItemsListDto,
  MatrixQuestionPayload,
  MatrixQuestionDetail,
  MatrixQuestionList,
  MatrixResource,
  MatrixResourcesDto,
  MatrixSheet,
  MatrixSheetsDto,
  mapMatrixDetailDto,
  mapMatrixListDto,
  mapMatrixResourceDto,
  mapMatrixSheetDto,
} from '../models/matrix-question.model';

@Injectable({ providedIn: 'root' })
export class MatrixService {
  private readonly api = inject(ApiClient);

  getPublicSheets(language: LanguageCode): Observable<MatrixSheet[]> {
    return this.api
      .get<MatrixSheetsDto>('/api/competency-matrix/sheets', { language })
      .pipe(map((dto) => dto.sheets.map(mapMatrixSheetDto)));
  }

  getAdminSheets(language: LanguageCode): Observable<MatrixSheet[]> {
    return this.api
      .get<MatrixSheetsDto>('/api/admin/competency-matrix/sheets', { language })
      .pipe(map((dto) => dto.sheets.map(mapMatrixSheetDto)));
  }

  getPublicQuestions(sheetKey: string, language: LanguageCode): Observable<MatrixQuestionList> {
    return this.api
      .get<MatrixItemsListDto>('/api/competency-matrix/items', {
        sheetKey,
        language,
      })
      .pipe(map(mapMatrixListDto));
  }

  getAdminQuestions(
    sheetKey: string,
    onlyPublished: boolean,
    language: LanguageCode,
  ): Observable<MatrixQuestionList> {
    return this.api
      .get<MatrixItemsListDto>('/api/admin/competency-matrix/items', {
        sheetKey,
        onlyPublished: String(onlyPublished),
        language,
      })
      .pipe(map(mapMatrixListDto));
  }

  getPublicQuestion(id: number, language: LanguageCode): Observable<MatrixQuestionDetail> {
    return this.api
      .get<MatrixItemDetailDto>(`/api/competency-matrix/items/detail/${id}`, { language })
      .pipe(map(mapMatrixDetailDto));
  }

  getAdminQuestion(
    id: number,
    onlyPublished: boolean,
    language: LanguageCode,
  ): Observable<MatrixQuestionDetail> {
    return this.api
      .get<MatrixItemDetailDto>(`/api/admin/competency-matrix/items/detail/${id}`, {
        onlyPublished: String(onlyPublished),
        language,
      })
      .pipe(map(mapMatrixDetailDto));
  }

  getPublicQuestionBySlug(slug: string, language: LanguageCode): Observable<MatrixQuestionDetail> {
    return this.api
      .get<MatrixItemDetailDto>(`/api/competency-matrix/items/public/${slug}`, { language })
      .pipe(map(mapMatrixDetailDto));
  }

  searchAdminResources(
    searchName: string,
    limit: number,
    language: LanguageCode,
  ): Observable<MatrixResource[]> {
    return this.api
      .get<MatrixResourcesDto>('/api/admin/competency-matrix/resources/search', {
        searchName,
        limit: String(limit),
        language,
      })
      .pipe(map((dto) => dto.resources.map(mapMatrixResourceDto)));
  }

  createAdminQuestion(
    payload: MatrixQuestionPayload,
    language: LanguageCode,
  ): Observable<MatrixQuestionDetail> {
    return this.api
      .post<MatrixItemDetailDto>('/api/admin/competency-matrix/items', payload, { language })
      .pipe(map(mapMatrixDetailDto));
  }

  suggestQuestion(question: string): Observable<void> {
    return this.api.post<void>('/api/competency-matrix/question-suggestions', { question });
  }

  updateAdminQuestion(
    id: number,
    payload: MatrixQuestionPayload,
    language: LanguageCode,
  ): Observable<MatrixQuestionDetail> {
    return this.api
      .put<MatrixItemDetailDto>(`/api/admin/competency-matrix/items/detail/${id}`, payload, {
        language,
      })
      .pipe(map(mapMatrixDetailDto));
  }

  publishAdminQuestion(id: number): Observable<void> {
    return this.api.post<void>(`/api/admin/competency-matrix/items/detail/${id}/set-published`, {});
  }

  unpublishAdminQuestion(id: number): Observable<void> {
    return this.api.post<void>(`/api/admin/competency-matrix/items/detail/${id}/set-draft`, {});
  }

  deleteAdminQuestion(id: number): Observable<void> {
    return this.api.delete<void>(`/api/admin/competency-matrix/items/detail/${id}`);
  }
}
