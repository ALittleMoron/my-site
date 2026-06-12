import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatrixGroupedListComponent } from './matrix-grouped-list.component';
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
            {
              grade: null,
              questions: [{ id: 2, slug: 'typing', question: 'What is typing?' }],
            },
          ],
        },
      ],
    },
  ],
};

describe('MatrixGroupedListComponent', () => {
  let fixture: ComponentFixture<MatrixGroupedListComponent>;
  let el: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatrixGroupedListComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixGroupedListComponent);
    fixture.componentRef.setInput('questions', questions);
    fixture.componentRef.setInput('notSetLabel', 'Not set');
    fixture.componentRef.setInput('gradeLabels', { Junior: 'Junior' });
    fixture.detectChanges();
    el = fixture.nativeElement as HTMLElement;
  });

  it('renders grouped sections, subsections, grades, and questions', () => {
    expect(el.textContent).toContain('Core');
    expect(el.textContent).toContain('Syntax');
    expect(el.textContent).toContain('Junior');
    expect(el.textContent).toContain('Not set');
    expect(el.textContent).toContain('What is PEP 8?');
  });

  it('emits selected question ids', () => {
    const emitted: number[] = [];
    fixture.componentInstance.questionSelected.subscribe((id) => emitted.push(id));

    el.querySelector<HTMLButtonElement>('button')?.click();

    expect(emitted).toEqual([1]);
  });
});
