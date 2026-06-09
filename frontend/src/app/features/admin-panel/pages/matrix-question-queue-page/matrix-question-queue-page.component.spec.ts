import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { ApiError } from '../../../../core/models/api-error.model';
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
    createQueuedQuestion: jest.Mock;
    rejectQueuedQuestion: jest.Mock;
    createQuestionFromQueue: jest.Mock;
  };
  let notificationService: { success: jest.Mock; error: jest.Mock };

  beforeEach(async () => {
    queueService = {
      listQueuedQuestions: jest.fn().mockReturnValue(of([queuedQuestion])),
      createQueuedQuestion: jest.fn().mockReturnValue(of(queuedQuestion)),
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

  it('renders manual add button next to refresh button', () => {
    const buttons = Array.from(
      fixture.nativeElement.querySelectorAll<HTMLButtonElement>(
        'h2 + div button, .d-flex > button',
      ),
    ).map((button) => button.textContent?.trim());

    expect(buttons).toContain('Добавить в очередь');
    expect(buttons).toContain('Обновить');
  });

  it('opens manual queue add modal with a one-line question input', () => {
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-open-manual-add"]')!
      .click();
    fixture.detectChanges();

    const input = fixture.nativeElement.querySelector<HTMLInputElement>(
      '#matrix-queue-manual-question',
    );

    expect(input).toBeTruthy();
    expect(input?.tagName).toBe('INPUT');
    expect(input?.type).toBe('text');
    expect(fixture.nativeElement.querySelector('textarea#matrix-queue-manual-question')).toBeNull();
  });

  it('disables manual queue submit for blank input', () => {
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-open-manual-add"]')!
      .click();
    fixture.detectChanges();

    const submitButton = fixture.nativeElement.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-queue-manual-submit"]',
    );

    expect(submitButton?.disabled).toBe(true);
  });

  it('normalizes multiline manual question text before adding it to the queue', () => {
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-open-manual-add"]')!
      .click();
    fixture.detectChanges();
    const input = fixture.nativeElement.querySelector<HTMLInputElement>(
      '#matrix-queue-manual-question',
    )!;
    const pasteEvent = new Event('paste') as ClipboardEvent;
    Object.defineProperty(pasteEvent, 'clipboardData', {
      value: {
        getData: (format: string) =>
          format === 'text' ? 'What is PEP 8?\nHow should it be used?' : '',
      },
    });
    input.dispatchEvent(pasteEvent);
    fixture.detectChanges();

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-manual-submit"]')!
      .click();

    expect(queueService.createQueuedQuestion).toHaveBeenCalledWith(
      'What is PEP 8? How should it be used?',
    );
  });

  it('closes manual queue modal and reloads queue after successful add', () => {
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-open-manual-add"]')!
      .click();
    fixture.detectChanges();
    const input = fixture.nativeElement.querySelector<HTMLInputElement>(
      '#matrix-queue-manual-question',
    )!;
    input.value = 'What is PEP 8?';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-manual-submit"]')!
      .click();
    fixture.detectChanges();

    expect(notificationService.success).toHaveBeenCalledWith('Вопрос добавлен в очередь.');
    expect(queueService.listQueuedQuestions).toHaveBeenCalledTimes(2);
    expect(fixture.nativeElement.querySelector('#matrix-queue-manual-question')).toBeNull();
  });

  it('keeps manual queue modal open and notifies when add fails', () => {
    const error: ApiError = {
      code: 'bad_request',
      type: 'bad_request',
      message: 'Failed',
      status: 400,
      location: null,
      attr: null,
    };
    queueService.createQueuedQuestion.mockReturnValue(throwError(() => error));
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-open-manual-add"]')!
      .click();
    fixture.detectChanges();
    const input = fixture.nativeElement.querySelector<HTMLInputElement>(
      '#matrix-queue-manual-question',
    )!;
    input.value = 'What is PEP 8?';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-manual-submit"]')!
      .click();
    fixture.detectChanges();

    expect(notificationService.error).toHaveBeenCalledWith('Не удалось добавить вопрос в очередь.');
    expect(fixture.nativeElement.querySelector('#matrix-queue-manual-question')).toBeTruthy();
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
