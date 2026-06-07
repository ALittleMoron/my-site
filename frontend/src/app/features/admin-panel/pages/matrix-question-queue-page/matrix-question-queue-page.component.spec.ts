import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { QueuedMatrixQuestion } from '../../models/matrix-question-queue.model';
import { MatrixQuestionQueueService } from '../../services/matrix-question-queue.service';
import { MatrixQuestionQueuePageComponent } from './matrix-question-queue-page.component';

const queuedQuestion: QueuedMatrixQuestion = {
  id: 7,
  question: 'What is PEP 8?',
  grade: 'Junior',
  sheet: 'Python',
  section: 'Core',
  subsection: 'Style',
  suggestedByUsername: null,
  createdAt: '2026-06-07T12:00:00+00:00',
};

describe('MatrixQuestionQueuePageComponent', () => {
  let fixture: ComponentFixture<MatrixQuestionQueuePageComponent>;
  let component: MatrixQuestionQueuePageComponent;
  let queueService: {
    listQueuedQuestions: jest.Mock;
    rejectQueuedQuestion: jest.Mock;
    createQuestionFromQueue: jest.Mock;
  };
  let notificationService: { success: jest.Mock; error: jest.Mock };

  beforeEach(async () => {
    queueService = {
      listQueuedQuestions: jest.fn().mockReturnValue(of([queuedQuestion])),
      rejectQueuedQuestion: jest.fn().mockReturnValue(of(undefined)),
      createQuestionFromQueue: jest.fn().mockReturnValue(of({ id: 1, slug: 'pep-8' })),
    };
    notificationService = {
      success: jest.fn(),
      error: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [MatrixQuestionQueuePageComponent],
      providers: [
        { provide: MatrixQuestionQueueService, useValue: queueService },
        { provide: NotificationService, useValue: notificationService },
        provideI18nTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixQuestionQueuePageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('renders queued questions from service', () => {
    expect(queueService.listQueuedQuestions).toHaveBeenCalled();
    expect(fixture.nativeElement.textContent).toContain('What is PEP 8?');
  });

  it('prefills create form from selected queued question', () => {
    component.selectQuestion(queuedQuestion);

    expect(component.form.getRawValue().questionRu).toBe('What is PEP 8?');
    expect(component.form.getRawValue().sheetKey).toBe('python');
  });

  it('marks selected queue question with green active styling', () => {
    component.selectQuestion(queuedQuestion);
    fixture.detectChanges();

    const selectedButton = fixture.nativeElement.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-queue-question-7"]',
    );

    expect(selectedButton).toBeTruthy();
    expect(selectedButton?.classList).toContain('list-group-item-success');
    expect(selectedButton?.classList).not.toContain('active');
    expect(selectedButton?.classList).not.toContain('list-group-item-primary');
  });

  it('rejects queued question and reloads queue', () => {
    component.rejectQuestion(queuedQuestion);

    expect(queueService.rejectQueuedQuestion).toHaveBeenCalledWith(7);
    expect(notificationService.success).toHaveBeenCalledWith('Вопрос отклонён.');
    expect(queueService.listQueuedQuestions).toHaveBeenCalledTimes(2);
  });

  it('creates matrix question from selected queue entry', () => {
    component.selectQuestion(queuedQuestion);
    component.form.patchValue({
      slug: 'pep-8',
      answerRu: 'Ответ',
      answerEn: 'Answer',
      expectedAnswerRu: 'Ожидаемый ответ',
      expectedAnswerEn: 'Expected answer',
    });

    component.createQuestion();

    expect(queueService.createQuestionFromQueue).toHaveBeenCalledWith(
      7,
      expect.objectContaining({
        slug: 'pep-8',
        sheetKey: 'python',
        grade: 'Junior',
        publishStatus: 'Draft',
        resources: [],
      }),
      'ru',
    );
  });
});
