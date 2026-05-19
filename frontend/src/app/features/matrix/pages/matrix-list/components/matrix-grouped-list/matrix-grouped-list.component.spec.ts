import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatrixGroupedListComponent } from './matrix-grouped-list.component';
import { MatrixQuestionList } from '../../../../models/matrix-question.model';

const mockQuestionList: MatrixQuestionList = {
  sheet: 'JavaScript',
  sections: [
    {
      section: 'Core',
      subsections: [
        {
          subsection: 'Syntax',
          grades: [
            {
              grade: 'Junior',
              questions: [
                { id: 1, question: 'What is a closure?' },
                { id: 2, question: 'What is hoisting?' },
              ],
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
    fixture.componentRef.setInput('questions', mockQuestionList);
    fixture.detectChanges();
    el = fixture.nativeElement as HTMLElement;
  });

  it('should render section heading', () => {
    expect(el.textContent).toContain('Core');
  });

  it('should render subsection heading', () => {
    expect(el.textContent).toContain('Syntax');
  });

  it('should render grade', () => {
    expect(el.textContent).toContain('Junior');
  });

  it('should render question text', () => {
    expect(el.textContent).toContain('What is a closure?');
  });

  it('should emit questionSelected with question id when clicked', () => {
    const emitted: number[] = [];
    fixture.componentInstance.questionSelected.subscribe((id: number) => emitted.push(id));
    const buttons = el.querySelectorAll<HTMLButtonElement>('button');
    buttons[0].click();
    expect(emitted).toEqual([1]);
  });
});
