import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { ReadonlyMatrixQuestionList } from '../matrix-readonly.model';

@Component({
  selector: 'app-matrix-readonly-grouped-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-grouped-list.component.html',
})
export class MatrixGroupedListComponent {
  readonly questions = input.required<ReadonlyMatrixQuestionList>();
  readonly gradeLabels = input<Record<string, string>>({});
  readonly notSetLabel = input.required<string>();

  readonly questionSelected = output<number>();

  selectQuestion(id: number): void {
    this.questionSelected.emit(id);
  }

  gradeLabel(grade: string | null): string {
    return grade === null ? this.notSetLabel() : (this.gradeLabels()[grade] ?? grade);
  }
}
