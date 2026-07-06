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

const QUESTION_ID = '00000000000000000000000000000007';
const IMPORTED_QUESTION_ID = '00000000000000000000000000000008';
const MISSING_SHEET_QUESTION_ID = '00000000000000000000000000000009';
const SHEET_ID = '00000000000000000000000000000001';
const SECTION_ID = '00000000000000000000000000000002';
const SUBSECTION_ID = '00000000000000000000000000000003';

const queuedQuestion: QueuedMatrixQuestion = {
  id: QUESTION_ID,
  question: 'What is PEP 8?',
  grade: 'Junior',
  sheet: 'python',
  section: 'Core',
  subsection: 'Style',
  suggestedByUsername: null,
  createdAt: '2026-06-07T12:00:00+00:00',
};

const importedQuestion: QueuedMatrixQuestion = {
  ...queuedQuestion,
  id: IMPORTED_QUESTION_ID,
  question: 'What is Black?',
};

const queuedQuestionWithMissingSheet: QueuedMatrixQuestion = {
  ...queuedQuestion,
  id: MISSING_SHEET_QUESTION_ID,
  sheet: 'sql',
};

const matrixStructure: AdminMatrixStructure = {
  sheets: [
    {
      id: SHEET_ID,
      key: 'python',
      name: 'Python',
      priority: 1,
      translations: { ru: { name: 'Питон' }, en: { name: 'Python' } },
      sections: [
        {
          id: SECTION_ID,
          name: 'Core',
          priority: 1,
          translations: { ru: { name: 'Основы' }, en: { name: 'Core' } },
          subsections: [
            {
              id: SUBSECTION_ID,
              name: 'Style',
              priority: 1,
              translations: { ru: { name: 'Стиль' }, en: { name: 'Style' } },
            },
          ],
        },
      ],
    },
  ],
};

const INVALID_SHORT_TEXT = 'x'.repeat(256);
const INVALID_MATRIX_TEXT = 'x'.repeat(20_001);

interface QueueCreateValidationCase {
  description: string;
  selector: string;
  expectedMessage: string;
  setInvalidValue: () => void;
}

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
      createQuestionFromQueue: jest.fn().mockReturnValue(of({ id: QUESTION_ID, slug: 'pep-8' })),
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

  it('keeps manual queue submit available and shows feedback for blank input', () => {
    openAddModal();

    const submitButton = fixture.nativeElement.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-queue-manual-submit"]',
    );

    expect(submitButton?.disabled).toBe(false);
    submitButton?.click();
    fixture.detectChanges();

    expect(queueService.createQueuedQuestion).not.toHaveBeenCalled();
    expectInvalidControl('#matrix-queue-manual-question', 'Заполните поле.');
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

  it('blocks too-long manual queue questions', () => {
    openAddModal();
    component.setManualAddQuestion(INVALID_SHORT_TEXT);
    fixture.detectChanges();

    component.createQueuedQuestion();
    fixture.detectChanges();

    expect(queueService.createQueuedQuestion).not.toHaveBeenCalled();
    expectInvalidControl('#matrix-queue-manual-question', 'Максимум 255 символов.');
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

  it('keeps import submit available and shows feedback until a file is selected', () => {
    openImportMode();

    const submitButton = fixture.nativeElement.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-queue-import-submit"]',
    );

    expect(submitButton?.disabled).toBe(false);
    submitButton?.click();
    fixture.detectChanges();

    expect(queueService.importQueuedQuestions).not.toHaveBeenCalled();
    expect(fixture.nativeElement.textContent).toContain('Выберите один файл.');
  });

  it('explains text and table import formats in import mode', () => {
    openImportMode();

    const text = fixture.nativeElement.textContent;

    expect(text).toContain('TXT: один вопрос на строку.');
    expect(text).toContain('CSV, XLSX и XLSM: колонки question, sheet, grade');
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

  it('shows feedback and keeps import submit retryable when more than one file is dropped', () => {
    openImportMode();
    dropImportFiles([
      new File(['first'], 'first.txt', { type: 'text/plain' }),
      new File(['second'], 'second.txt', { type: 'text/plain' }),
    ]);

    const submitButton = fixture.nativeElement.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-queue-import-submit"]',
    );

    expect(fixture.nativeElement.textContent).toContain('Выберите один файл.');
    expect(submitButton?.disabled).toBe(false);
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
    fixture.detectChanges();

    expect(component.form.getRawValue().questionRu).toBe('What is PEP 8?');
    expect(component.form.getRawValue().subsectionId).toBeNull();
    expect(select('[data-testid="matrix-structure-sheet"]').value).toBe(SHEET_ID);
  });

  it('highlights a missing queued sheet key and pre-fills sheet creation', () => {
    component.selectQuestion(queuedQuestionWithMissingSheet);
    fixture.detectChanges();

    expect(select('[data-testid="matrix-structure-sheet"]').value).toBe('');
    expect(fixture.nativeElement.textContent).toContain(
      'Лист с ключом sql не найден. Создайте лист и заполните названия RU/EN.',
    );
    expect(inputValue('[data-testid="matrix-structure-sheet-key"]')).toBe('sql');
    expect(inputValue('[data-testid="matrix-structure-sheet-ru"]')).toBe('');
    expect(inputValue('[data-testid="matrix-structure-sheet-en"]')).toBe('');
  });

  it('lays out queue create fields for the narrow queue column', () => {
    component.selectQuestion(queuedQuestion);
    fixture.detectChanges();

    expect(fieldColumn('#queue-question-slug').classList).toContain('col-12');
    expect(fieldColumn('#queue-question-slug').classList).toContain('col-md-8');
    expect(fieldColumn('#queue-question-grade').classList).toContain('col-12');
    expect(fieldColumn('#queue-question-grade').classList).toContain('col-md-4');

    for (const selector of [
      '#queue-question-ru',
      '#queue-question-en',
      '#queue-answer-ru',
      '#queue-answer-en',
      '#queue-expected-answer-ru',
      '#queue-expected-answer-en',
    ]) {
      const column = fieldColumn(selector);
      expect(column.classList).toContain('col-12');
      expect(column.classList).not.toContain('col-md-6');
    }
  });

  it('marks selected queue question with green active styling', () => {
    component.selectQuestion(queuedQuestion);
    fixture.detectChanges();

    const selectedButton = fixture.nativeElement.querySelector<HTMLButtonElement>(
      `[data-testid="matrix-queue-question-${QUESTION_ID}"]`,
    );

    expect(selectedButton).toBeTruthy();
    expect(selectedButton?.classList).toContain('list-group-item-success');
    expect(selectedButton?.classList).not.toContain('active');
    expect(selectedButton?.classList).not.toContain('list-group-item-primary');
  });

  it('rejects queued question and reloads queue', () => {
    component.rejectQuestion(queuedQuestion);

    expect(queueService.rejectQueuedQuestion).toHaveBeenCalledWith(QUESTION_ID);
    expect(notificationService.success).toHaveBeenCalledWith('Вопрос отклонён.');
    expect(queueService.listQueuedQuestions).toHaveBeenCalledTimes(2);
  });

  it('creates matrix question from selected queue entry', () => {
    component.selectQuestion(queuedQuestion);
    component.form.patchValue({
      slug: 'pep-8',
      subsectionId: SUBSECTION_ID,
      answerRu: 'Ответ',
      answerEn: 'Answer',
      expectedAnswerRu: 'Ожидаемый ответ',
      expectedAnswerEn: 'Expected answer',
    });

    component.createQuestion();

    expect(queueService.createQuestionFromQueue).toHaveBeenCalledWith(
      QUESTION_ID,
      expect.objectContaining({
        slug: 'pep-8',
        subsectionId: SUBSECTION_ID,
        grade: 'Junior',
        publishStatus: 'Draft',
        resources: [],
      }),
      'ru',
    );
  });

  it('blocks invalid queue create payload before calling the service', () => {
    component.selectQuestion(queuedQuestion);
    component.form.patchValue({
      slug: 'Invalid Slug',
      subsectionId: SUBSECTION_ID,
      answerRu: 'Ответ',
      answerEn: 'Answer',
      expectedAnswerRu: 'Ожидаемый ответ',
      expectedAnswerEn: 'Expected answer',
    });

    component.createQuestion();

    expect(queueService.createQuestionFromQueue).not.toHaveBeenCalled();
  });

  it.each<QueueCreateValidationCase>([
    {
      description: 'slug pattern',
      selector: '#queue-question-slug',
      expectedMessage: 'Используйте строчные латинские буквы, цифры и одинарные дефисы.',
      setInvalidValue: () => setInput('#queue-question-slug', 'Invalid Slug'),
    },
    {
      description: 'subsection required',
      selector: '[data-testid="matrix-structure-subsection"]',
      expectedMessage: 'Выберите подраздел.',
      setInvalidValue: () => component.form.controls.subsectionId.setValue(null),
    },
    {
      description: 'grade required',
      selector: '#queue-question-grade',
      expectedMessage: 'Заполните поле.',
      setInvalidValue: () => component.form.controls.grade.setValue('' as AdminMatrixGrade),
    },
    {
      description: 'question RU required text',
      selector: '#queue-question-ru',
      expectedMessage: 'Заполните поле.',
      setInvalidValue: () => setInput('#queue-question-ru', '   '),
    },
    {
      description: 'question EN max length',
      selector: '#queue-question-en',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => setInput('#queue-question-en', INVALID_SHORT_TEXT),
    },
    {
      description: 'answer RU required text',
      selector: '#queue-answer-ru',
      expectedMessage: 'Заполните поле.',
      setInvalidValue: () => setInput('#queue-answer-ru', '   '),
    },
    {
      description: 'answer EN max length',
      selector: '#queue-answer-en',
      expectedMessage: 'Максимум 20000 символов.',
      setInvalidValue: () => setInput('#queue-answer-en', INVALID_MATRIX_TEXT),
    },
    {
      description: 'expected answer RU required text',
      selector: '#queue-expected-answer-ru',
      expectedMessage: 'Заполните поле.',
      setInvalidValue: () => setInput('#queue-expected-answer-ru', '   '),
    },
    {
      description: 'expected answer EN max length',
      selector: '#queue-expected-answer-en',
      expectedMessage: 'Максимум 20000 символов.',
      setInvalidValue: () => setInput('#queue-expected-answer-en', INVALID_MATRIX_TEXT),
    },
  ])('shows invalid styling and localized feedback for $description', (validationCase) => {
    fillValidQueueCreateForm();
    validationCase.setInvalidValue();
    fixture.detectChanges();

    component.createQuestion();
    fixture.detectChanges();

    expect(queueService.createQuestionFromQueue).not.toHaveBeenCalled();
    expectInvalidControl(validationCase.selector, validationCase.expectedMessage);
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

  function fillValidQueueCreateForm(): void {
    component.selectQuestion(queuedQuestion);
    fixture.detectChanges();
    component.form.patchValue({
      slug: 'pep-8',
      subsectionId: SUBSECTION_ID,
      grade: 'Junior',
      questionRu: 'Что такое PEP 8?',
      questionEn: 'What is PEP 8?',
      answerRu: 'Ответ',
      answerEn: 'Answer',
      expectedAnswerRu: 'Ожидаемый ответ',
      expectedAnswerEn: 'Expected answer',
    });
    fixture.detectChanges();
  }

  function setInput(selector: string, value: string): void {
    const input = fixture.nativeElement.querySelector(selector) as
      HTMLInputElement | HTMLTextAreaElement;
    input.value = value;
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  function inputValue(selector: string): string {
    const input = fixture.nativeElement.querySelector(selector) as HTMLInputElement | null;
    if (input === null) {
      throw new Error(`Missing queue form input: ${selector}`);
    }
    return input.value;
  }

  function select(selector: string): HTMLSelectElement {
    const element = fixture.nativeElement.querySelector(selector) as HTMLSelectElement | null;
    if (element === null) {
      throw new Error(`Missing queue form select: ${selector}`);
    }
    return element;
  }

  function expectInvalidControl(selector: string, expectedMessage: string): void {
    const element = fixture.nativeElement.querySelector(selector) as HTMLElement | null;
    expect(element).not.toBeNull();
    expect(element?.classList).toContain('is-invalid');
    expect(element?.getAttribute('aria-invalid')).toBe('true');
    expect(fixture.nativeElement.textContent).toContain(expectedMessage);
  }

  function fieldColumn(selector: string): HTMLElement {
    const field = fixture.nativeElement.querySelector(selector) as HTMLElement | null;
    if (field === null) {
      throw new Error(`Missing queue create form field: ${selector}`);
    }
    const column = field.closest<HTMLElement>('.col-12, .col-md-4, .col-md-6, .col-md-8');
    if (column === null) {
      throw new Error(`Missing queue create form column for: ${selector}`);
    }
    return column;
  }
});
