import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { ApiError } from '../../../../core/models/api-error.model';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { AdminMatrixStructure } from '../../models/matrix-question-workspace.model';
import { QueuedMatrixQuestion } from '../../models/matrix-question-queue.model';
import { MatrixQuestionWorkspaceService } from '../../services/matrix-question-workspace.service';
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

const importedQuestion: QueuedMatrixQuestion = {
  ...queuedQuestion,
  id: 8,
  question: 'What is Black?',
};

const matrixStructure: AdminMatrixStructure = {
  sheets: [
    {
      id: 1,
      key: 'python',
      name: 'Python',
      translations: { ru: { name: 'Питон' }, en: { name: 'Python' } },
      sections: [
        {
          id: 2,
          name: 'Core',
          translations: { ru: { name: 'Основы' }, en: { name: 'Core' } },
          subsections: [
            {
              id: 3,
              name: 'Style',
              translations: { ru: { name: 'Стиль' }, en: { name: 'Style' } },
            },
          ],
        },
      ],
    },
  ],
};

describe('MatrixQuestionQueuePageComponent', () => {
  let fixture: ComponentFixture<MatrixQuestionQueuePageComponent>;
  let component: MatrixQuestionQueuePageComponent;
  let queueService: {
    listQueuedQuestions: jest.Mock;
    createQueuedQuestion: jest.Mock;
    importQueuedQuestions: jest.Mock;
    rejectQueuedQuestion: jest.Mock;
    createQuestionFromQueue: jest.Mock;
  };
  let workspaceService: jest.Mocked<MatrixQuestionWorkspaceService>;
  let notificationService: { success: jest.Mock; error: jest.Mock };

  beforeEach(async () => {
    queueService = {
      listQueuedQuestions: jest.fn().mockReturnValue(of([queuedQuestion])),
      createQueuedQuestion: jest.fn().mockReturnValue(of(queuedQuestion)),
      importQueuedQuestions: jest.fn().mockReturnValue(of([queuedQuestion, importedQuestion])),
      rejectQueuedQuestion: jest.fn().mockReturnValue(of(undefined)),
      createQuestionFromQueue: jest.fn().mockReturnValue(of({ id: '1', slug: 'pep-8' })),
    };
    workspaceService = {
      getStructure: jest.fn().mockReturnValue(of(matrixStructure)),
      createSheet: jest.fn(),
      createSection: jest.fn(),
      createSubsection: jest.fn(),
    } as unknown as jest.Mocked<MatrixQuestionWorkspaceService>;
    notificationService = {
      success: jest.fn(),
      error: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [MatrixQuestionQueuePageComponent],
      providers: [
        { provide: MatrixQuestionQueueService, useValue: queueService },
        { provide: MatrixQuestionWorkspaceService, useValue: workspaceService },
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
    openAddModal();

    const input = fixture.nativeElement.querySelector<HTMLInputElement>(
      '#matrix-queue-manual-question',
    );

    expect(input).toBeTruthy();
    expect(input?.tagName).toBe('INPUT');
    expect(input?.type).toBe('text');
    expect(fixture.nativeElement.querySelector('textarea#matrix-queue-manual-question')).toBeNull();
  });

  it('switches queue add modal between manual input and import upload', () => {
    openAddModal();

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-import-mode"]')!
      .click();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('#matrix-queue-manual-question')).toBeNull();
    expect(
      fixture.nativeElement.querySelector<HTMLInputElement>(
        '[data-testid="matrix-queue-import-file-input"]',
      ),
    ).toBeTruthy();
    expect(
      fixture.nativeElement.querySelector<HTMLElement>(
        '[data-testid="matrix-queue-import-drop-zone"]',
      ),
    ).toBeTruthy();

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-manual-mode"]')!
      .click();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('#matrix-queue-manual-question')).toBeTruthy();
  });

  it('disables manual queue submit for blank input', () => {
    openAddModal();

    const submitButton = fixture.nativeElement.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-queue-manual-submit"]',
    );

    expect(submitButton?.disabled).toBe(true);
  });

  it('normalizes multiline manual question text before adding it to the queue', () => {
    openAddModal();
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
    openAddModal();
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
    openAddModal();
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

  it('disables import submit until a file is selected', () => {
    openImportMode();

    const submitButton = fixture.nativeElement.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-queue-import-submit"]',
    );

    expect(submitButton?.disabled).toBe(true);
  });

  it('selects one import file from file input', () => {
    openImportMode();
    chooseImportFile(new File(['question'], 'questions.txt', { type: 'text/plain' }));

    expect(fixture.nativeElement.textContent).toContain('Выбран файл: questions.txt');
  });

  it('selects one import file from drop zone', () => {
    openImportMode();
    dropImportFiles([new File(['question'], 'questions.csv', { type: 'text/csv' })]);

    expect(fixture.nativeElement.textContent).toContain('Выбран файл: questions.csv');
  });

  it('keeps import submit disabled when more than one file is dropped', () => {
    openImportMode();
    dropImportFiles([
      new File(['first'], 'first.txt', { type: 'text/plain' }),
      new File(['second'], 'second.txt', { type: 'text/plain' }),
    ]);

    const submitButton = fixture.nativeElement.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-queue-import-submit"]',
    );

    expect(fixture.nativeElement.textContent).toContain('Выберите один файл.');
    expect(submitButton?.disabled).toBe(true);
  });

  it('closes import modal, reloads queue, and shows imported count after success', () => {
    openImportMode();
    const file = new File(['question'], 'questions.txt', { type: 'text/plain' });
    chooseImportFile(file);

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-import-submit"]')!
      .click();
    fixture.detectChanges();

    expect(queueService.importQueuedQuestions).toHaveBeenCalledWith(file);
    expect(notificationService.success).toHaveBeenCalledWith('Импортировано вопросов: 2.');
    expect(queueService.listQueuedQuestions).toHaveBeenCalledTimes(2);
    expect(
      fixture.nativeElement.querySelector('[data-testid="matrix-queue-import-file-input"]'),
    ).toBeNull();
  });

  it('keeps import modal open and renders backend nested errors when import fails', () => {
    const error: ApiError = {
      code: 'bad_request',
      type: 'bad_request',
      message: 'Question queue import file is invalid.',
      status: 400,
      location: null,
      attr: null,
      nested_errors: [
        {
          code: 'bad_request',
          type: 'bad_request',
          message: 'Row 2: question must not be empty.',
          status: 400,
          location: 'body',
          attr: 'row_2',
        },
      ],
    };
    queueService.importQueuedQuestions.mockReturnValue(throwError(() => error));
    openImportMode();
    chooseImportFile(new File(['question'], 'questions.txt', { type: 'text/plain' }));

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-import-submit"]')!
      .click();
    fixture.detectChanges();

    expect(notificationService.error).toHaveBeenCalledWith('Не удалось импортировать вопросы.');
    expect(
      fixture.nativeElement.querySelector('[data-testid="matrix-queue-import-file-input"]'),
    ).toBeTruthy();
    expect(fixture.nativeElement.textContent).not.toContain(
      'Question queue import file is invalid.',
    );
    expect(fixture.nativeElement.textContent).toContain('Row 2: question must not be empty.');
  });

  it('prefills create form from selected queued question', () => {
    component.selectQuestion(queuedQuestion);

    expect(component.form.getRawValue().questionRu).toBe('What is PEP 8?');
    expect(component.form.getRawValue().subsectionId).toBeNull();
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
      subsectionId: 3,
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
        subsectionId: 3,
        grade: 'Junior',
        publishStatus: 'Draft',
        resources: [],
      }),
      'ru',
    );
  });

  function openAddModal(): void {
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-open-manual-add"]')!
      .click();
    fixture.detectChanges();
  }

  function openImportMode(): void {
    openAddModal();
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-queue-import-mode"]')!
      .click();
    fixture.detectChanges();
  }

  function chooseImportFile(file: File): void {
    const input = fixture.nativeElement.querySelector<HTMLInputElement>(
      '[data-testid="matrix-queue-import-file-input"]',
    )!;
    Object.defineProperty(input, 'files', {
      value: [file],
      configurable: true,
    });
    input.dispatchEvent(new Event('change'));
    fixture.detectChanges();
  }

  function dropImportFiles(files: File[]): void {
    const dropZone = fixture.nativeElement.querySelector<HTMLElement>(
      '[data-testid="matrix-queue-import-drop-zone"]',
    )!;
    const event = new Event('drop', { bubbles: true }) as DragEvent;
    Object.defineProperty(event, 'dataTransfer', {
      value: { files },
    });
    dropZone.dispatchEvent(event);
    fixture.detectChanges();
  }
});
