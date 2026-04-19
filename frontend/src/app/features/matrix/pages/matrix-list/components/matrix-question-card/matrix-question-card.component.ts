import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { MatrixQuestion } from '../../../../models/matrix-question.model';

@Component({
  selector: 'app-matrix-question-card',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-question-card.component.html',
})
export class MatrixQuestionCardComponent {
  readonly question = input.required<MatrixQuestion>();
}
