import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import { LanguageCode } from '../../../core/i18n/i18n.model';
import {
  AdminMatrixItemDetailDto,
  AdminMatrixItemPayload,
  QueuedMatrixQuestion,
  QueuedMatrixQuestionDto,
  QueuedMatrixQuestionsDto,
  mapQueuedMatrixQuestionDto,
} from '../models/matrix-question-queue.model';

@Injectable({ providedIn: 'root' })
export class MatrixQuestionQueueService {
  private readonly api = inject(ApiClient);

  listQueuedQuestions(): Observable<QueuedMatrixQuestion[]> {
    return this.api
      .get<QueuedMatrixQuestionsDto>('/api/competency-matrix/queued-questions')
      .pipe(map((dto) => dto.questions.map(mapQueuedMatrixQuestionDto)));
  }

  createQueuedQuestion(question: string): Observable<QueuedMatrixQuestion> {
    return this.api
      .post<QueuedMatrixQuestionDto>('/api/competency-matrix/queued-questions', { question })
      .pipe(map(mapQueuedMatrixQuestionDto));
  }

  rejectQueuedQuestion(questionId: number): Observable<void> {
    return this.api.delete<void>(`/api/competency-matrix/queued-questions/${questionId}`);
  }

  createQuestionFromQueue(
    questionId: number,
    payload: AdminMatrixItemPayload,
    language: LanguageCode,
  ): Observable<AdminMatrixItemDetailDto> {
    return this.api.post<AdminMatrixItemDetailDto>(
      `/api/competency-matrix/queued-questions/${questionId}/create-item`,
      payload,
      { language },
    );
  }
}
