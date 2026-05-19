import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import {
  MatrixItemDetailDto,
  MatrixItemsListDto,
  MatrixQuestionDetail,
  MatrixQuestionList,
  MatrixSheetsDto,
  mapMatrixDetailDto,
  mapMatrixListDto,
} from '../models/matrix-question.model';

@Injectable({ providedIn: 'root' })
export class MatrixService {
  private readonly api = inject(ApiClient);

  getSheets(): Observable<string[]> {
    return this.api
      .get<MatrixSheetsDto>('/api/competency-matrix/sheets')
      .pipe(map(dto => dto.sheets));
  }

  getQuestions(sheetName: string, onlyPublished: boolean): Observable<MatrixQuestionList> {
    return this.api
      .get<MatrixItemsListDto>('/api/competency-matrix/items', {
        sheetName,
        onlyPublished: String(onlyPublished),
      })
      .pipe(map(mapMatrixListDto));
  }

  getQuestion(id: number, onlyPublished: boolean): Observable<MatrixQuestionDetail> {
    return this.api
      .get<MatrixItemDetailDto>(`/api/competency-matrix/items/detail/${id}`, {
        onlyPublished: String(onlyPublished),
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
