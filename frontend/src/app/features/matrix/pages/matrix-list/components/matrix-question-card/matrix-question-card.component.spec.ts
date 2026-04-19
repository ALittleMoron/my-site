import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatrixQuestionCardComponent } from './matrix-question-card.component';
import { MatrixQuestion } from '../../../../models/matrix-question.model';

const mockQuestion: MatrixQuestion = {
  id: '1',
  title: 'What is a closure?',
  description: 'Explain JS closures.',
  grade: 'junior',
  topic: 'JavaScript',
  is_published: true,
};

describe('MatrixQuestionCardComponent', () => {
  let fixture: ComponentFixture<MatrixQuestionCardComponent>;
  let el: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatrixQuestionCardComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixQuestionCardComponent);
    fixture.componentRef.setInput('question', mockQuestion);
    fixture.detectChanges();
    el = fixture.nativeElement as HTMLElement;
  });

  it('should render question title', () => {
    expect(el.textContent).toContain('What is a closure?');
  });

  it('should render grade', () => {
    expect(el.textContent).toContain('junior');
  });

  it('should render topic', () => {
    expect(el.textContent).toContain('JavaScript');
  });
});
