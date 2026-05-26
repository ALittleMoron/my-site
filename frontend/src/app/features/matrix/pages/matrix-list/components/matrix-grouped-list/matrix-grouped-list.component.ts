import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { MatrixQuestionList } from '../../../../models/matrix-question.model';

@Component({
  selector: 'app-matrix-grouped-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-grouped-list.component.html',
})
export class MatrixGroupedListComponent {
  readonly questions = input.required<MatrixQuestionList>();

  readonly questionSelected = output<number>();

  selectQuestion(id: number): void {
    this.questionSelected.emit(id);
  }
}
