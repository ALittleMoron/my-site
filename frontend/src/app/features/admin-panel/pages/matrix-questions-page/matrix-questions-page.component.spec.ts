import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { Router, provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { MatrixQuestionFormComponent } from '../../components/matrix-question-form/matrix-question-form.component';
import {
  AdminMatrixQuestionDetailDto,
  AdminMatrixQuestionWorkspace,
  AdminMatrixResource,
  AdminMatrixStructure,
  AdminMatrixWorkspaceFilterOptions,
  AdminReadonlyMatrixQuestionList,
  AdminReadonlyMatrixSheet,
} from '../../models/matrix-question-workspace.model';
import { MatrixQuestionWorkspaceService } from '../../services/matrix-question-workspace.service';
import { MatrixQuestionsPageComponent } from './matrix-questions-page.component';

const QUESTION_ID = '00000000000000000000000000000007';
const READY_QUESTION_ID = '00000000000000000000000000000008';
const SAVED_QUESTION_ID = '00000000000000000000000000000009';
const SHEET_ID = '00000000000000000000000000000001';
const SECTION_ID = '00000000000000000000000000000002';
const SUBSECTION_ID = '00000000000000000000000000000003';
const RESOURCE_ID = '00000000000000000000000000000004';

const workspace: AdminMatrixQuestionWorkspace = {
  totalCount: 2,
  totalPages: 1,
  summary: {
    total: 2,
    draft: 1,
    missingDraft: 1,
    dangerousPublished: 0,
    readyPublished: 1,
  },
  items: [
    {
      id: QUESTION_ID,
      slug: 'typing',
      question: 'What is typing?',
      sheetKey: 'python',
      sheet: 'Python',
      grade: 'Junior',
      interviewFrequency: 'often',
      section: 'Core',
      subsection: 'Syntax',
      publishStatus: 'Draft',
      publishedAt: null,
      missingFields: ['answerEn'],
    },
    {
      id: READY_QUESTION_ID,
      slug: 'ready-question',
      question: 'Ready question?',
      sheetKey: 'python',
      sheet: 'Python',
      grade: 'Middle',
      interviewFrequency: 'rarely',
      section: 'Core',
      subsection: 'Syntax',
      publishStatus: 'Published',
      publishedAt: '2026-01-02T00:00:00+00:00',
      missingFields: [],
    },
  ],
};

const options: AdminMatrixWorkspaceFilterOptions = {
  sheets: [
    {
      key: 'python',
      label: 'Python',
      sections: [{ label: 'Core', subsections: ['Syntax'] }],
    },
    {
      key: 'sql',
      label: 'SQL',
      sections: [{ label: 'Queries', subsections: ['Select'] }],
    },
  ],
  grades: ['Junior', 'Middle'],
  interviewFrequencies: ['often', 'rarely'],
  sections: ['Core', 'Queries'],
  subsections: ['Syntax', 'Select'],
  publishStatuses: ['Draft', 'Published'],
};

const savedQuestion: AdminMatrixQuestionDetailDto = {
  id: SAVED_QUESTION_ID,
  slug: 'new-question',
  question: 'New question?',
  answer: '',
  interviewExpectedAnswer: '',
  subsectionId: SUBSECTION_ID,
  sheetKey: 'python',
  sheet: '',
  grade: null,
  interviewFrequency: null,
  section: '',
  subsection: '',
  publishStatus: 'Draft',
  suggestedByUsername: 'owner',
  translations: {
    ru: {
      question: 'Новый вопрос?',
      answer: '',
      interviewExpectedAnswer: '',
    },
    en: {
      question: 'New question?',
      answer: '',
      interviewExpectedAnswer: '',
    },
  },
  resources: [],
};

const resource: AdminMatrixResource = {
  id: RESOURCE_ID,
  name: 'Python docs',
  url: 'https://docs.python.org',
  translations: {
    ru: { name: 'Документация Python' },
    en: { name: 'Python docs' },
  },
};

const previewSheets: AdminReadonlyMatrixSheet[] = [{ key: 'python', name: 'Python' }];
const matrixStructure: AdminMatrixStructure = {
  sheets: [
    {
      id: SHEET_ID,
      key: 'python',
      name: 'Питон',
      priority: 1,
      translations: { ru: { name: 'Питон' }, en: { name: 'Python' } },
      sections: [
        {
          id: SECTION_ID,
          name: 'Основы',
          priority: 1,
          translations: { ru: { name: 'Основы' }, en: { name: 'Core' } },
          subsections: [
            {
              id: SUBSECTION_ID,
              name: 'Стиль',
              priority: 1,
              translations: { ru: { name: 'Стиль' }, en: { name: 'Style' } },
            },
          ],
        },
      ],
    },
  ],
};
const previewQuestions: AdminReadonlyMatrixQuestionList = {
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
              questions: [
                {
                  slug: 'typing',
                  question: 'What is typing?',
                  interviewFrequency: 'often',
                },
              ],
            },
          ],
        },
      ],
    },
  ],
};

describe('MatrixQuestionsPageComponent', () => {
  let fixture: ComponentFixture<MatrixQuestionsPageComponent>;
  let service: jest.Mocked<MatrixQuestionWorkspaceService>;
  let router: Router;
  let notifications: { success: jest.Mock; error: jest.Mock };

  beforeEach(async () => {
    service = {
      listWorkspaceItems: jest.fn().mockReturnValue(of(workspace)),
      getFilterOptions: jest.fn().mockReturnValue(of(options)),
      listPublicPreviewSheets: jest.fn().mockReturnValue(of(previewSheets)),
      listPublicPreviewQuestions: jest.fn().mockReturnValue(of(previewQuestions)),
      deleteQuestion: jest.fn().mockReturnValue(of(void 0)),
      publishQuestion: jest.fn().mockReturnValue(of(void 0)),
      unpublishQuestion: jest.fn().mockReturnValue(of(void 0)),
      getStructure: jest.fn().mockReturnValue(of(matrixStructure)),
      createSheet: jest.fn(),
      createSection: jest.fn(),
      createSubsection: jest.fn(),
      getQuestion: jest.fn(),
      createQuestion: jest.fn().mockReturnValue(of(savedQuestion)),
      updateQuestion: jest.fn().mockReturnValue(of(savedQuestion)),
      searchResources: jest.fn().mockReturnValue(of([resource])),
    } as unknown as jest.Mocked<MatrixQuestionWorkspaceService>;
    notifications = { success: jest.fn(), error: jest.fn() };

    await TestBed.configureTestingModule({
      imports: [MatrixQuestionsPageComponent],
      providers: [
        provideI18nTesting(),
        provideRouter([]),
        { provide: MatrixQuestionWorkspaceService, useValue: service },
        { provide: NotificationService, useValue: notifications },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixQuestionsPageComponent);
    router = TestBed.inject(Router);
    jest.spyOn(router, 'navigate').mockResolvedValue(true);
    fixture.detectChanges();
  });

  it('loads workspace counters and compact rows', () => {
    expect(service.getFilterOptions).toHaveBeenCalledWith('ru');
    expect(service.listWorkspaceItems).toHaveBeenCalled();
    expect(fixture.nativeElement.textContent).toContain('Всего');
    expect(fixture.nativeElement.textContent).toContain('Опасно опубликованы');
    expect(fixture.nativeElement.textContent).toContain('What is typing?');
    expect(fixture.nativeElement.textContent).toContain('Часто');
    expect(fixture.nativeElement.textContent).toContain('answerEn');
  });

  it('links only ready published questions to the public question page', () => {
    const links = Array.from(fixture.nativeElement.querySelectorAll('a')).map(
      (link) => (link as HTMLAnchorElement).getAttribute('href') ?? '',
    );

    expect(links).toContain('/ru/competency-matrix/questions/ready-question');
    expect(links).not.toContain('/ru/competency-matrix/questions/typing');
    expect(
      fixture.nativeElement.querySelector('[title*="Публичная страница"]')?.textContent,
    ).toContain('What is typing?');
  });

  it('applies and resets filters', () => {
    const search = fixture.nativeElement.querySelector(
      '[data-testid="matrix-workspace-search"]',
    ) as HTMLInputElement;
    search.value = 'typing';
    search.dispatchEvent(new Event('input'));
    const frequency = fixture.nativeElement.querySelector(
      '#matrix-workspace-interview-frequency',
    ) as HTMLSelectElement;
    frequency.value = 'rarely';
    frequency.dispatchEvent(new Event('change'));
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-workspace-apply"]')
      ?.click();

    expect(lastWorkspaceFilters().searchQuery).toBe('typing');
    expect(lastWorkspaceFilters().interviewFrequencies).toEqual(['rarely']);

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-workspace-reset"]')
      ?.click();

    expect(lastWorkspaceFilters().searchQuery).toBeUndefined();
    expect(lastWorkspaceFilters().interviewFrequencies).toBeUndefined();
    expect(lastWorkspaceFilters().page).toBe(1);
  });

  it('loads public preview only after opening the preview tab', () => {
    expect(service.listPublicPreviewSheets).not.toHaveBeenCalled();

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-workspace-preview-tab"]')
      ?.click();
    fixture.detectChanges();

    expect(service.listPublicPreviewSheets).toHaveBeenCalledWith('ru');
    expect(service.listPublicPreviewQuestions).toHaveBeenCalledWith('python', 'ru');
    expect(fixture.nativeElement.textContent).toContain('What is typing?');
    expect(fixture.nativeElement.querySelector('app-matrix-readonly-grouped-grid')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('app-matrix-readonly-grouped-list')).toBeNull();
  });

  it('disables and resets dependent section filters from selected sheet and section', () => {
    const sheet = fixture.nativeElement.querySelector(
      '#matrix-workspace-sheet',
    ) as HTMLSelectElement;
    const section = fixture.nativeElement.querySelector(
      '#matrix-workspace-section',
    ) as HTMLSelectElement;
    const subsection = fixture.nativeElement.querySelector(
      '#matrix-workspace-subsection',
    ) as HTMLSelectElement;

    expect(section.disabled).toBe(true);
    expect(subsection.disabled).toBe(true);

    sheet.value = 'python';
    sheet.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    expect(section.disabled).toBe(false);
    expect(section.textContent).toContain('Core');
    expect(section.textContent).not.toContain('Queries');

    section.value = 'Core';
    section.dispatchEvent(new Event('change'));
    fixture.detectChanges();
    expect(subsection.disabled).toBe(false);
    expect(subsection.textContent).toContain('Syntax');

    sheet.value = 'sql';
    sheet.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    expect(section.value).toBe('');
    expect(subsection.value).toBe('');
    expect(section.textContent).toContain('Queries');
    expect(section.textContent).not.toContain('Core');
  });

  it('marks required fields and clears red border after a required value is entered', () => {
    fixture.componentInstance.openCreate();
    fixture.detectChanges();

    const slug = fixture.nativeElement.querySelector('#matrix-form-slug') as HTMLInputElement;

    expect(fixture.nativeElement.textContent).toContain('Slug *');
    saveButton().click();
    fixture.detectChanges();
    expect(slug.classList).toContain('is-invalid');

    slug.value = 'draft-question';
    slug.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(slug.classList).not.toContain('is-invalid');
  });

  it('saves an incomplete draft with only the minimum required fields', () => {
    fixture.componentInstance.openCreate();
    fixture.detectChanges();
    setInput('#matrix-form-slug', 'draft-question');
    selectQuestionSubsection(SUBSECTION_ID);
    setInput('#matrix-form-question-ru', 'Неполный вопрос?');
    setInput('#matrix-form-question-en', 'Incomplete question?');

    saveButton().click();

    const payload = service.createQuestion.mock.calls[0][0];
    expect(payload.subsectionId).toBe(SUBSECTION_ID);
    expect('sheetKey' in payload).toBe(false);
    expect(payload.grade).toBeNull();
    expect(payload.interviewFrequency).toBeNull();
    expect(payload.publishStatus).toBe('Draft');
    expect(payload.translations.ru.answer).toBe('');
    expect(payload.resources).toEqual([]);
  });

  it('saves the selected interview frequency from the admin form', () => {
    fixture.componentInstance.openCreate();
    fixture.detectChanges();
    setInput('#matrix-form-slug', 'frequent-question');
    selectQuestionSubsection(SUBSECTION_ID);
    setInput('#matrix-form-question-ru', 'Частый вопрос?');
    setInput('#matrix-form-question-en', 'Frequent question?');
    const frequency = fixture.nativeElement.querySelector(
      '#matrix-form-interview-frequency',
    ) as HTMLSelectElement;
    frequency.value = 'often';
    frequency.dispatchEvent(new Event('change'));

    saveButton().click();

    expect(service.createQuestion.mock.calls[0][0].interviewFrequency).toBe('often');
  });

  it('warns and skips the publish API for incomplete workspace rows', () => {
    openRowActions(QUESTION_ID);
    fixture.nativeElement
      .querySelector<HTMLButtonElement>(`[data-testid="matrix-actions-${QUESTION_ID}-publish"]`)
      ?.click();

    expect(service.publishQuestion).not.toHaveBeenCalled();
    expect(notifications.error.mock.calls[0][0]).toContain('answerEn');
  });

  it('routes the row edit action to the matrix question detail page', () => {
    service.getQuestion.mockReturnValue(of(savedQuestion));

    openRowActions(QUESTION_ID);
    fixture.nativeElement
      .querySelector<HTMLButtonElement>(`[data-testid="matrix-actions-${QUESTION_ID}-edit"]`)
      ?.click();
    fixture.detectChanges();

    expect(router.navigate).toHaveBeenCalledWith(['/admin-panel/matrix-questions', QUESTION_ID]);
    expect(service.getQuestion).not.toHaveBeenCalled();
  });

  it('adds, searches, edits context, and removes resources in the admin form', () => {
    fixture.componentInstance.openCreate();
    fixture.detectChanges();

    setInput('[data-testid="matrix-resource-search"]', 'python');
    fixture.detectChanges();

    expect(service.searchResources).toHaveBeenCalledWith('python', 10, 'ru');
    fixture.nativeElement
      .querySelector<HTMLButtonElement>(`[data-testid="matrix-resource-attach-${RESOURCE_ID}"]`)
      ?.click();
    fixture.detectChanges();
    setTextarea('#matrixResourceContextRu0', 'Читать');
    setTextarea('#matrixResourceContextEn0', 'Read');

    setInput('[data-testid="matrix-resource-new-name-ru"]', 'Новый ресурс');
    setInput('[data-testid="matrix-resource-new-name-en"]', 'New resource');
    setInput('[data-testid="matrix-resource-new-url"]', 'https://example.com');
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-resource-add-new"]')
      ?.click();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Новый ресурс');

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-resource-detach-1"]')
      ?.click();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).not.toContain('Новый ресурс');

    setInput('#matrix-form-slug', 'draft-question');
    selectQuestionSubsection(SUBSECTION_ID);
    setInput('#matrix-form-question-ru', 'Вопрос?');
    setInput('#matrix-form-question-en', 'Question?');
    saveButton().click();

    expect(service.createQuestion.mock.calls[0][0].resources).toEqual([
      {
        resourceId: RESOURCE_ID,
        translations: { ru: { context: 'Читать' }, en: { context: 'Read' } },
      },
    ]);
  });

  it('renders structure picker instead of manual taxonomy text fields', () => {
    fixture.componentInstance.openCreate();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('app-matrix-structure-picker')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('#matrix-form-sheet-key')).toBeNull();
    expect(fixture.nativeElement.querySelector('#matrix-form-sheet-ru')).toBeNull();
    expect(fixture.nativeElement.querySelector('#matrix-form-section-ru')).toBeNull();
    expect(fixture.nativeElement.querySelector('#matrix-form-subsection-ru')).toBeNull();
  });

  it('generates slug only from the explicit button action', () => {
    fixture.componentInstance.openCreate();
    fixture.detectChanges();
    const slug = fixture.nativeElement.querySelector('#matrix-form-slug') as HTMLInputElement;
    const generateButton = Array.from(fixture.nativeElement.querySelectorAll('button')).find(
      (button): button is HTMLButtonElement =>
        (button as HTMLButtonElement).textContent?.includes('Сгенерировать') ?? false,
    );

    expect(generateButton?.disabled).toBe(true);
    setInput('#matrix-form-question-en', 'What is dependency injection?');
    fixture.detectChanges();

    expect(slug.value).toBe('');
    expect(generateButton?.disabled).toBe(false);
    generateButton?.click();
    fixture.detectChanges();

    expect(slug.value).toBe('what-is-dependency-injection');
  });

  it('confirms deletes before calling the admin delete endpoint', () => {
    jest.spyOn(window, 'confirm').mockReturnValue(true);

    openRowActions(QUESTION_ID);
    fixture.nativeElement
      .querySelector<HTMLButtonElement>(`[data-testid="matrix-actions-${QUESTION_ID}-delete"]`)
      ?.click();

    expect(window.confirm).toHaveBeenCalled();
    expect(service.deleteQuestion).toHaveBeenCalledWith(QUESTION_ID);
  });

  function lastWorkspaceFilters(): Parameters<
    MatrixQuestionWorkspaceService['listWorkspaceItems']
  >[0] {
    const filters = service.listWorkspaceItems.mock.calls.at(-1)?.[0];
    if (filters === undefined) {
      throw new Error('No workspace request');
    }
    return filters;
  }

  function openRowActions(id: string): void {
    fixture.nativeElement
      .querySelector<HTMLButtonElement>(`[data-testid="matrix-actions-${id}-toggle"]`)
      ?.click();
    fixture.detectChanges();
  }

  function selectQuestionSubsection(subsectionId: string): void {
    const form = fixture.debugElement.query(By.directive(MatrixQuestionFormComponent))
      .componentInstance as MatrixQuestionFormComponent;
    form.selectQuestionSubsection(subsectionId);
    fixture.detectChanges();
  }

  function setInput(selector: string, value: string): void {
    const input = fixture.nativeElement.querySelector(selector) as HTMLInputElement;
    input.value = value;
    input.dispatchEvent(new Event('input'));
  }

  function setTextarea(selector: string, value: string): void {
    const textarea = fixture.nativeElement.querySelector(selector) as HTMLTextAreaElement;
    textarea.value = value;
    textarea.dispatchEvent(new Event('input'));
  }

  function saveButton(): HTMLButtonElement {
    const button = fixture.nativeElement.querySelector(
      '[data-testid="matrix-form-save"]',
    ) as HTMLButtonElement | null;
    if (button === null) {
      throw new Error('No matrix form save button');
    }
    return button;
  }
});
