import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatrixGroupedGridComponent } from './matrix-grouped-grid.component';
import { ReadonlyMatrixQuestionList } from '../matrix-readonly.model';

const questions: ReadonlyMatrixQuestionList = {
  sheetKey: 'python',
  sheet: 'Python',
  sections: [
    {
      section: 'Core',
      subsections: [
        {
          subsection: 'Syntax',
          grades: [
            {
              grade: 'Junior',
              questions: [{ id: 1, slug: 'pep-8', question: 'What is PEP 8?' }],
            },
          ],
        },
      ],
    },
  ],
};

describe('MatrixGroupedGridComponent', () => {
  let fixture: ComponentFixture<MatrixGroupedGridComponent>;
  let el: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatrixGroupedGridComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixGroupedGridComponent);
    fixture.componentRef.setInput('questions', questions);
    fixture.componentRef.setInput('sectionLabel', 'Section');
    fixture.componentRef.setInput('subsectionLabel', 'Subsection');
    fixture.componentRef.setInput('notSetLabel', 'Not set');
    fixture.componentRef.setInput('gradeLabels', { Junior: 'Junior' });
    fixture.detectChanges();
    el = fixture.nativeElement as HTMLElement;
  });

  it('renders table headings and question buttons', () => {
    expect(el.textContent).toContain('Section');
    expect(el.textContent).toContain('Subsection');
    expect(el.textContent).toContain('Junior');
    expect(el.textContent).toContain('What is PEP 8?');
  });

  it('emits selected question ids', () => {
    const emitted: number[] = [];
    fixture.componentInstance.questionSelected.subscribe((id) => emitted.push(id));

    el.querySelector<HTMLButtonElement>('button')?.click();

    expect(emitted).toEqual([1]);
  });
});
