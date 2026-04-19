import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import { MatrixQuestion } from '../models/matrix-question.model';

@Injectable({ providedIn: 'root' })
export class MatrixService {
  private readonly api = inject(ApiClient);

  getQuestions(search?: string): Observable<MatrixQuestion[]> {
    const params = search ? { search } : undefined;
    return this.api.get<MatrixQuestion[]>('/api/matrix/questions', params);
  }

  getQuestion(id: string): Observable<MatrixQuestion> {
    return this.api.get<MatrixQuestion>(`/api/matrix/questions/${id}`);
  }
}
