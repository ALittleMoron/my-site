import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { MatrixGroupedGridComponent } from './matrix-grouped-grid.component';
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
              questions: [{ id: 1, question: 'What is a closure?' }],
            },
            {
              grade: 'Middle',
              questions: [{ id: 2, question: 'What is a generator?' }],
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
      providers: [provideI18nTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixGroupedGridComponent);
    fixture.componentRef.setInput('questions', mockQuestionList);
    fixture.detectChanges();
    el = fixture.nativeElement as HTMLElement;
  });

  it('should render table', () => {
    expect(el.querySelector('table')).toBeTruthy();
  });

  it('should render grade headers', () => {
    const headers = el.querySelectorAll('th');
    const headerText = Array.from(headers).map((h) => h.textContent?.trim());
    expect(headerText).toContain('Раздел');
    expect(headerText).toContain('Подраздел');
    expect(headerText).toContain('Junior');
    expect(headerText).toContain('Middle');
  });

  it('should use legacy matrix table styling classes', () => {
    expect(el.querySelector('.competency-matrix-table-container')).not.toBeNull();
    expect(el.querySelector('table')?.classList).toContain('competency-matrix-table');
  });

  it('should render section name', () => {
    expect(el.textContent).toContain('Core');
  });

  it('should render question text', () => {
    expect(el.textContent).toContain('What is a closure?');
  });

  it('should emit questionSelected with id when question clicked', () => {
    const emitted: number[] = [];
    fixture.componentInstance.questionSelected.subscribe((id: number) => emitted.push(id));
    const button = el.querySelector<HTMLButtonElement>('button')!;
    button.click();
    expect(emitted).toEqual([1]);
  });
});
