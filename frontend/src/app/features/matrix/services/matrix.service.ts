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

  getSheets(language: LanguageCode): Observable<MatrixSheet[]> {
    return this.api
      .get<MatrixSheetsDto>('/api/competency-matrix/sheets', { language })
      .pipe(map((dto) => dto.sheets.map(mapMatrixSheetDto)));
  }

  getQuestions(
    sheetKey: string,
    onlyPublished: boolean,
    language: LanguageCode,
  ): Observable<MatrixQuestionList> {
    return this.api
      .get<MatrixItemsListDto>('/api/competency-matrix/items', {
        sheetKey,
        onlyPublished: String(onlyPublished),
        language,
      })
      .pipe(map(mapMatrixListDto));
  }

  getQuestion(
    id: number,
    onlyPublished: boolean,
    language: LanguageCode,
  ): Observable<MatrixQuestionDetail> {
    return this.api
      .get<MatrixItemDetailDto>(`/api/competency-matrix/items/detail/${id}`, {
        onlyPublished: String(onlyPublished),
        language,
      })
      .pipe(map(mapMatrixDetailDto));
  }

  getPublicQuestion(slug: string, language: LanguageCode): Observable<MatrixQuestionDetail> {
    return this.api
      .get<MatrixItemDetailDto>(`/api/competency-matrix/items/public/${slug}`, { language })
      .pipe(map(mapMatrixDetailDto));
  }

  searchResources(
    searchName: string,
    limit: number,
    language: LanguageCode,
  ): Observable<MatrixResource[]> {
    return this.api
      .get<MatrixResourcesDto>('/api/competency-matrix/resources/search', {
        searchName,
        limit: String(limit),
        language,
      })
      .pipe(map((dto) => dto.resources.map(mapMatrixResourceDto)));
  }

  createQuestion(
    payload: MatrixQuestionPayload,
    language: LanguageCode,
  ): Observable<MatrixQuestionDetail> {
    return this.api
      .post<MatrixItemDetailDto>('/api/competency-matrix/items', payload, { language })
      .pipe(map(mapMatrixDetailDto));
  }

  suggestQuestion(question: string): Observable<void> {
    return this.api.post<void>('/api/competency-matrix/question-suggestions', { question });
  }

  updateQuestion(
    id: number,
    payload: MatrixQuestionPayload,
    language: LanguageCode,
  ): Observable<MatrixQuestionDetail> {
    return this.api
      .put<MatrixItemDetailDto>(`/api/competency-matrix/items/detail/${id}`, payload, {
        language,
      })
      .pipe(map(mapMatrixDetailDto));
  }

  publishQuestion(id: number): Observable<void> {
    return this.api.post<void>(`/api/competency-matrix/items/detail/${id}/set-published`, {});
  }

  unpublishQuestion(id: number): Observable<void> {
    return this.api.post<void>(`/api/competency-matrix/items/detail/${id}/set-draft`, {});
  }

  deleteQuestion(id: number): Observable<void> {
    return this.api.delete<void>(`/api/competency-matrix/items/detail/${id}`);
  }
}
