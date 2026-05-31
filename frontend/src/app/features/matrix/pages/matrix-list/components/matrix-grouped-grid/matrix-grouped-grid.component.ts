import { Component, ChangeDetectionStrategy, input, output, computed } from '@angular/core';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import {
  MatrixQuestion,
  MatrixQuestionList,
  MatrixSectionGroup,
} from '../../../../models/matrix-question.model';

interface GridCell {
  grade: string | null;
  questions: MatrixQuestion[];
}

interface GridRow {
  section: MatrixSectionGroup;
  subsection: string;
  isFirstSubsection: boolean;
  sectionRowspan: number;
  cells: GridCell[];
}

@Component({
  selector: 'app-matrix-grouped-grid',
  standalone: true,
  imports: [TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-grouped-grid.component.html',
})
export class MatrixGroupedGridComponent {
  readonly questions = input.required<MatrixQuestionList>();

  readonly questionSelected = output<number>();

  readonly grades = computed<(string | null)[]>(() => {
    const seen = new Set<string | null>();
    const result: (string | null)[] = [];
    for (const section of this.questions().sections) {
      for (const subsection of section.subsections) {
        for (const grade of subsection.grades) {
          if (!seen.has(grade.grade)) {
            seen.add(grade.grade);
            result.push(grade.grade);
          }
        }
      }
    }
    return result;
  });

  readonly rows = computed<GridRow[]>(() => {
    const gradeList = this.grades();
    const result: GridRow[] = [];
    for (const section of this.questions().sections) {
      for (let i = 0; i < section.subsections.length; i++) {
        const subsection = section.subsections[i];
        const cells: GridCell[] = gradeList.map((gradeName) => {
          const gradeGroup = subsection.grades.find((g) => g.grade === gradeName);
          return { grade: gradeName, questions: gradeGroup ? gradeGroup.questions : [] };
        });
        result.push({
          section,
          subsection: subsection.subsection,
          isFirstSubsection: i === 0,
          sectionRowspan: section.subsections.length,
          cells,
        });
      }
    }
    return result;
  });

  selectQuestion(id: number): void {
    this.questionSelected.emit(id);
  }

  gradeLabelKey(grade: string | null): string {
    if (grade === null) return 'shared.notSet';
    return `enum.grade.${grade.replace('+', 'Plus')}`;
  }
}
