import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { MatrixQuestionList } from '../../../../models/matrix-question.model';

@Component({
  selector: 'app-matrix-grouped-list',
  standalone: true,
  imports: [TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-grouped-list.component.html',
})
export class MatrixGroupedListComponent {
  readonly questions = input.required<MatrixQuestionList>();

  readonly questionSelected = output<number>();

  selectQuestion(id: number): void {
    this.questionSelected.emit(id);
  }

  gradeLabelKey(grade: string | null): string {
    if (grade === null) return 'shared.notSet';
    return `enum.grade.${grade.replace('+', 'Plus')}`;
  }
}
