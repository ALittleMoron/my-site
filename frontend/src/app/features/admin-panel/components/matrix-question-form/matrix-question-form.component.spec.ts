import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { MarkdownEditorComponent } from '../../../../core/editor/markdown-editor.component';
import {
  AdminMatrixQuestionDetailDto,
  AdminMatrixQuestionPayload,
  AdminMatrixResource,
} from '../../models/matrix-question-workspace.model';
import { MatrixQuestionWorkspaceService } from '../../services/matrix-question-workspace.service';
import { MatrixStructurePickerComponent } from '../matrix-structure-picker/matrix-structure-picker.component';
import { MatrixQuestionFormComponent } from './matrix-question-form.component';

const RESOURCE_ID = '00000000000000000000000000000003';
const SUBSECTION_ID = '00000000000000000000000000000013';

const resource: AdminMatrixResource = {
  id: RESOURCE_ID,
  name: 'Python docs',
  url: 'https://docs.python.org',
  translations: {
    ru: { name: 'Документация Python' },
    en: { name: 'Python docs' },
  },
};

const INVALID_SHORT_TEXT = 'x'.repeat(256);
const INVALID_MATRIX_TEXT = 'x'.repeat(20_001);
const VALID_RESOURCE_URL = 'https://example.com/docs';

interface MatrixQuestionControlValidationCase {
  description: string;
  selector: string;
  expectedMessage: string;
  setInvalidValue: () => void;
}

describe('MatrixQuestionFormComponent', () => {
  let fixture: ComponentFixture<MatrixQuestionFormComponent>;
  let service: jest.Mocked<MatrixQuestionWorkspaceService>;
  let emittedPayloads: AdminMatrixQuestionPayload[];

  beforeEach(async () => {
    service = {
      searchResources: jest.fn().mockReturnValue(of([resource])),
    } as unknown as jest.Mocked<MatrixQuestionWorkspaceService>;
    emittedPayloads = [];

    await TestBed.configureTestingModule({
      imports: [MatrixQuestionFormComponent],
      providers: [
        provideI18nTesting(),
        { provide: MatrixQuestionWorkspaceService, useValue: service },
      ],
    })
      .overrideComponent(MatrixQuestionFormComponent, {
        remove: { imports: [MatrixStructurePickerComponent, MarkdownEditorComponent] },
        add: { imports: [MatrixStructurePickerStubComponent, MarkdownEditorStubComponent] },
      })
      .compileComponents();

    fixture = TestBed.createComponent(MatrixQuestionFormComponent);
    fixture.componentRef.setInput('mode', 'create');
    fixture.componentRef.setInput('question', null);
    fixture.componentRef.setInput('createInitialValue', null);
    fixture.componentRef.setInput('submitting', false);
    fixture.componentInstance.questionSave.subscribe((payload) => emittedPayloads.push(payload));
    fixture.detectChanges();
  });

  it('marks required fields and clears the red border after a required value is entered', () => {
    const slug = fixture.nativeElement.querySelector('#matrix-form-slug') as HTMLInputElement;

    expect(fixture.nativeElement.textContent).toContain('Slug *');
    submitForm();
    fixture.detectChanges();
    expect(slug.classList).toContain('is-invalid');

    slug.value = 'draft-question';
    slug.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(slug.classList).not.toContain('is-invalid');
  });

  it.each<MatrixQuestionControlValidationCase>([
    {
      description: 'slug pattern',
      selector: '#matrix-form-slug',
      expectedMessage: 'Используйте строчные латинские буквы, цифры и одинарные дефисы.',
      setInvalidValue: () => setInput('#matrix-form-slug', 'Invalid Slug'),
    },
    {
      description: 'question RU required text',
      selector: '#matrix-form-question-ru',
      expectedMessage: 'Заполните поле.',
      setInvalidValue: () => setInput('#matrix-form-question-ru', '   '),
    },
    {
      description: 'question EN max length',
      selector: '#matrix-form-question-en',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => setInput('#matrix-form-question-en', INVALID_SHORT_TEXT),
    },
    {
      description: 'answer RU max length',
      selector: '#matrix-form-answer-ru',
      expectedMessage: 'Максимум 20000 символов.',
      setInvalidValue: () => setMarkdownEditor('#matrix-form-answer-ru', INVALID_MATRIX_TEXT),
    },
    {
      description: 'answer EN max length',
      selector: '#matrix-form-answer-en',
      expectedMessage: 'Максимум 20000 символов.',
      setInvalidValue: () => setMarkdownEditor('#matrix-form-answer-en', INVALID_MATRIX_TEXT),
    },
    {
      description: 'expected answer RU max length',
      selector: '#matrix-form-expected-ru',
      expectedMessage: 'Максимум 20000 символов.',
      setInvalidValue: () => setMarkdownEditor('#matrix-form-expected-ru', INVALID_MATRIX_TEXT),
    },
    {
      description: 'expected answer EN max length',
      selector: '#matrix-form-expected-en',
      expectedMessage: 'Максимум 20000 символов.',
      setInvalidValue: () => setMarkdownEditor('#matrix-form-expected-en', INVALID_MATRIX_TEXT),
    },
  ])('shows invalid styling and localized feedback for $description', (validationCase) => {
    fillValidQuestionMinimum();
    validationCase.setInvalidValue();

    submitForm();

    expect(emittedPayloads).toEqual([]);
    expectInvalidControl(validationCase.selector, validationCase.expectedMessage);
  });

  it('shows invalid styling and localized feedback for the required subsection picker', () => {
    setInput('#matrix-form-slug', 'draft-question');
    setInput('#matrix-form-question-ru', 'Вопрос?');
    setInput('#matrix-form-question-en', 'Question?');

    submitForm();

    expect(emittedPayloads).toEqual([]);
    expect(fixture.nativeElement.textContent).toContain('Выберите подраздел.');
    expectInvalidControl('[data-testid="matrix-structure-subsection"]', 'Выберите подраздел.');
  });

  it('emits an incomplete draft payload with only minimum required fields', () => {
    setInput('#matrix-form-slug', 'draft-question');
    selectQuestionSubsection(SUBSECTION_ID);
    setInput('#matrix-form-question-ru', 'Неполный вопрос?');
    setInput('#matrix-form-question-en', 'Incomplete question?');

    submitForm();

    expect(emittedPayloads[0]).toEqual(
      expect.objectContaining({
        subsectionId: SUBSECTION_ID,
        grade: null,
        interviewFrequency: null,
        publishStatus: 'Draft',
        translations: expect.objectContaining({
          ru: expect.objectContaining({ answer: '' }),
        }),
        resources: [],
      }),
    );
  });

  it('prefills create form from explicit initial value', () => {
    fixture.componentRef.setInput('createInitialValue', {
      slug: 'queued-question-0007',
      subsectionId: null,
      preferredSheetKey: 'python',
      grade: 'Junior',
      interviewFrequency: null,
      publishStatus: 'Draft',
      translations: {
        ru: {
          question: 'Что такое PEP 8?',
          answer: '',
          interviewExpectedAnswer: '',
        },
        en: {
          question: 'What is PEP 8?',
          answer: '',
          interviewExpectedAnswer: '',
        },
      },
    });
    fixture.detectChanges();

    expect(inputValue('#matrix-form-slug')).toBe('queued-question-0007');
    expect(inputValue('#matrix-form-question-ru')).toBe('Что такое PEP 8?');
    expect(inputValue('#matrix-form-question-en')).toBe('What is PEP 8?');
    expect(selectValue('#matrix-form-grade')).toBe('Junior');
    expect(
      fixture.debugElement.query(By.directive(MatrixStructurePickerStubComponent)).componentInstance
        .preferredSheetKey,
    ).toBe('python');
  });

  it('edits answer and expected-answer Markdown through shared editors', () => {
    fixture.componentRef.setInput('createInitialValue', {
      slug: 'queued-question-0007',
      subsectionId: SUBSECTION_ID,
      preferredSheetKey: 'python',
      grade: 'Junior',
      interviewFrequency: null,
      publishStatus: 'Draft',
      translations: {
        ru: {
          question: 'Что такое PEP 8?',
          answer: '## RU answer',
          interviewExpectedAnswer: 'RU expected',
        },
        en: {
          question: 'What is PEP 8?',
          answer: '## EN answer',
          interviewExpectedAnswer: 'EN expected',
        },
      },
    });
    fixture.detectChanges();

    const editors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));

    expect(editors).toHaveLength(4);
    expect(editors.map((editor) => editor.componentInstance.value)).toEqual([
      '## RU answer',
      '## EN answer',
      'RU expected',
      'EN expected',
    ]);

    editors[0].componentInstance.valueChange.emit('Updated RU answer');
    editors[1].componentInstance.valueChange.emit('Updated EN answer');
    editors[2].componentInstance.valueChange.emit('Updated RU expected');
    editors[3].componentInstance.valueChange.emit('Updated EN expected');
    fixture.detectChanges();

    submitForm();

    expect(emittedPayloads[0].translations).toEqual({
      ru: {
        question: 'Что такое PEP 8?',
        answer: 'Updated RU answer',
        interviewExpectedAnswer: 'Updated RU expected',
      },
      en: {
        question: 'What is PEP 8?',
        answer: 'Updated EN answer',
        interviewExpectedAnswer: 'Updated EN expected',
      },
    });
  });

  it('shows both localized field sets by default', () => {
    fixture.componentRef.setInput('createInitialValue', {
      slug: 'queued-question-0007',
      subsectionId: SUBSECTION_ID,
      preferredSheetKey: 'python',
      grade: 'Junior',
      interviewFrequency: null,
      publishStatus: 'Draft',
      translations: {
        ru: {
          question: 'Что такое PEP 8?',
          answer: '## RU answer',
          interviewExpectedAnswer: 'RU expected',
        },
        en: {
          question: 'What is PEP 8?',
          answer: '## EN answer',
          interviewExpectedAnswer: 'EN expected',
        },
      },
    });
    fixture.detectChanges();

    expect(inputValue('#matrix-form-question-ru')).toBe('Что такое PEP 8?');
    expect(inputValue('#matrix-form-question-en')).toBe('What is PEP 8?');
    expect(element('#matrix-form-answer-ru')).not.toBeNull();
    expect(element('#matrix-form-answer-en')).not.toBeNull();
    expect(element('#matrix-form-expected-ru')).not.toBeNull();
    expect(element('#matrix-form-expected-en')).not.toBeNull();
    expect(
      fixture.nativeElement
        .querySelector('[data-testid="matrix-form-display-mode-ru-en"]')
        ?.getAttribute('aria-pressed'),
    ).toBe('true');
    expect(
      fixture.debugElement
        .queryAll(By.directive(MarkdownEditorStubComponent))
        .map((editor) => editor.componentInstance.value),
    ).toEqual(['## RU answer', '## EN answer', 'RU expected', 'EN expected']);
  });

  it('switches between RU and EN localized field sets without losing values', () => {
    fixture.componentRef.setInput('createInitialValue', {
      slug: 'queued-question-0007',
      subsectionId: SUBSECTION_ID,
      preferredSheetKey: 'python',
      grade: 'Junior',
      interviewFrequency: null,
      publishStatus: 'Draft',
      translations: {
        ru: {
          question: 'Что такое PEP 8?',
          answer: '## RU answer',
          interviewExpectedAnswer: 'RU expected',
        },
        en: {
          question: 'What is PEP 8?',
          answer: '## EN answer',
          interviewExpectedAnswer: 'EN expected',
        },
      },
    });
    fixture.detectChanges();

    clickDisplayMode('ru');
    expect(inputValue('#matrix-form-question-ru')).toBe('Что такое PEP 8?');
    expect(element('#matrix-form-question-en')).toBeNull();
    expect(element('#matrix-form-answer-ru')).not.toBeNull();
    expect(element('#matrix-form-answer-en')).toBeNull();
    expect(element('#matrix-form-expected-ru')).not.toBeNull();
    expect(element('#matrix-form-expected-en')).toBeNull();
    setInput('#matrix-form-question-ru', 'Что такое PEP 8 на практике?');
    setMarkdownEditor('#matrix-form-answer-ru', 'Updated RU answer');
    setMarkdownEditor('#matrix-form-expected-ru', 'Updated RU expected');

    clickDisplayMode('en');
    expect(element('#matrix-form-question-ru')).toBeNull();
    expect(inputValue('#matrix-form-question-en')).toBe('What is PEP 8?');
    expect(element('#matrix-form-answer-ru')).toBeNull();
    expect(element('#matrix-form-answer-en')).not.toBeNull();
    expect(element('#matrix-form-expected-ru')).toBeNull();
    expect(element('#matrix-form-expected-en')).not.toBeNull();
    setInput('#matrix-form-question-en', 'What is PEP 8 in practice?');
    setMarkdownEditor('#matrix-form-answer-en', 'Updated EN answer');
    setMarkdownEditor('#matrix-form-expected-en', 'Updated EN expected');

    clickDisplayMode('ru-en');
    expect(inputValue('#matrix-form-question-ru')).toBe('Что такое PEP 8 на практике?');
    expect(inputValue('#matrix-form-question-en')).toBe('What is PEP 8 in practice?');

    submitForm();

    expect(emittedPayloads[0].translations).toEqual({
      ru: {
        question: 'Что такое PEP 8 на практике?',
        answer: 'Updated RU answer',
        interviewExpectedAnswer: 'Updated RU expected',
      },
      en: {
        question: 'What is PEP 8 in practice?',
        answer: 'Updated EN answer',
        interviewExpectedAnswer: 'Updated EN expected',
      },
    });
  });

  it('returns to RU+EN when hidden localized fields block submission', () => {
    fillValidQuestionMinimum();
    setInput('#matrix-form-question-en', INVALID_SHORT_TEXT);
    clickDisplayMode('ru');

    submitForm();

    expect(emittedPayloads).toEqual([]);
    expect(element('#matrix-form-question-en')).not.toBeNull();
    expect(
      fixture.nativeElement
        .querySelector('[data-testid="matrix-form-display-mode-ru-en"]')
        ?.getAttribute('aria-pressed'),
    ).toBe('true');
    expectInvalidControl('#matrix-form-question-en', 'Максимум 255 символов.');
  });

  it('blocks invalid slug and long answer text before emitting', () => {
    setInput('#matrix-form-slug', 'Invalid Slug');
    selectQuestionSubsection(SUBSECTION_ID);
    setInput('#matrix-form-question-ru', 'Вопрос?');
    setInput('#matrix-form-question-en', 'Question?');

    submitForm();

    expect(emittedPayloads).toEqual([]);

    setInput('#matrix-form-slug', 'valid-question');
    setMarkdownEditor('#matrix-form-answer-en', 'x'.repeat(20_001));

    submitForm();

    expect(emittedPayloads).toEqual([]);
  });

  it('blocks an incomplete published payload before emitting', () => {
    setInput('#matrix-form-slug', 'draft-question');
    selectQuestionSubsection(SUBSECTION_ID);
    setInput('#matrix-form-question-ru', 'Неполный вопрос?');
    setInput('#matrix-form-question-en', 'Incomplete question?');
    setSelect('#matrix-form-status', 'Published');

    submitForm();

    expect(emittedPayloads).toEqual([]);
    expect(fixture.nativeElement.textContent).toContain('Нельзя опубликовать вопрос');
  });

  it('generates slug only from the explicit button action', () => {
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

  it('lays out metadata, question text, and multiline fields in readable rows', () => {
    fixture.componentInstance.attachResource(resource);
    fixture.detectChanges();

    expect(fieldColumn('#matrix-form-grade').classList).toContain('col-md-4');
    expect(fieldColumn('#matrix-form-interview-frequency').classList).toContain('col-md-4');
    expect(fieldColumn('#matrix-form-status').classList).toContain('col-md-4');
    expect(fieldColumn('#matrix-form-question-ru').classList).toContain('col-md-6');
    expect(fieldColumn('#matrix-form-question-en').classList).toContain('col-md-6');

    for (const selector of [
      '#matrix-form-answer-ru',
      '#matrix-form-answer-en',
      '#matrix-form-expected-ru',
      '#matrix-form-expected-en',
      '#matrixResourceContextRu0',
      '#matrixResourceContextEn0',
    ]) {
      const column = fieldColumn(selector);
      expect(column.classList).toContain('col-12');
      expect(column.classList).not.toContain('col-md-6');
    }
  });

  it('blocks invalid new resource URL and too-long resource context', () => {
    setInput('[data-testid="matrix-resource-new-name-ru"]', 'Документация');
    setInput('[data-testid="matrix-resource-new-name-en"]', 'Documentation');
    setInput('[data-testid="matrix-resource-new-url"]', 'ftp://example.com/docs');
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-resource-add-new"]')
      ?.click();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).not.toContain('ftp://example.com/docs');

    fixture.nativeElement
      .querySelector<HTMLInputElement>('[data-testid="matrix-resource-search"]')!
      .dispatchEvent(new Event('input'));
    fixture.componentInstance.attachResource(resource);
    fixture.detectChanges();
    setTextarea('#matrixResourceContextEn0', 'x'.repeat(20_001));
    setInput('#matrix-form-slug', 'draft-question');
    selectQuestionSubsection(SUBSECTION_ID);
    setInput('#matrix-form-question-ru', 'Вопрос?');
    setInput('#matrix-form-question-en', 'Question?');

    submitForm();

    expect(emittedPayloads).toEqual([]);
  });

  it.each<MatrixQuestionControlValidationCase>([
    {
      description: 'new resource RU name',
      selector: '[data-testid="matrix-resource-new-name-ru"]',
      expectedMessage: 'Заполните поле.',
      setInvalidValue: () => {
        setInput('[data-testid="matrix-resource-new-name-en"]', 'Documentation');
        setInput('[data-testid="matrix-resource-new-url"]', VALID_RESOURCE_URL);
      },
    },
    {
      description: 'new resource EN name',
      selector: '[data-testid="matrix-resource-new-name-en"]',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => {
        setInput('[data-testid="matrix-resource-new-name-ru"]', 'Документация');
        setInput('[data-testid="matrix-resource-new-name-en"]', INVALID_SHORT_TEXT);
        setInput('[data-testid="matrix-resource-new-url"]', VALID_RESOURCE_URL);
      },
    },
    {
      description: 'new resource URL',
      selector: '[data-testid="matrix-resource-new-url"]',
      expectedMessage: 'Укажите ссылку с http или https.',
      setInvalidValue: () => {
        setInput('[data-testid="matrix-resource-new-name-ru"]', 'Документация');
        setInput('[data-testid="matrix-resource-new-name-en"]', 'Documentation');
        setInput('[data-testid="matrix-resource-new-url"]', 'ftp://example.com/docs');
      },
    },
  ])('shows invalid styling and localized feedback for $description', (validationCase) => {
    validationCase.setInvalidValue();

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-resource-add-new"]')
      ?.click();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).not.toContain(VALID_RESOURCE_URL);
    expectInvalidControl(validationCase.selector, validationCase.expectedMessage);
  });

  it.each<MatrixQuestionControlValidationCase>([
    {
      description: 'resource RU context',
      selector: '#matrixResourceContextRu0',
      expectedMessage: 'Максимум 20000 символов.',
      setInvalidValue: () => setTextarea('#matrixResourceContextRu0', INVALID_MATRIX_TEXT),
    },
    {
      description: 'resource EN context',
      selector: '#matrixResourceContextEn0',
      expectedMessage: 'Максимум 20000 символов.',
      setInvalidValue: () => setTextarea('#matrixResourceContextEn0', INVALID_MATRIX_TEXT),
    },
  ])('shows invalid styling and localized feedback for $description', (validationCase) => {
    fixture.componentInstance.attachResource(resource);
    fixture.detectChanges();
    fillValidQuestionMinimum();
    validationCase.setInvalidValue();

    submitForm();

    expect(emittedPayloads).toEqual([]);
    expectInvalidControl(validationCase.selector, validationCase.expectedMessage);
  });

  it('adds, searches, edits context, and removes resources in the form payload', () => {
    setInput('[data-testid="matrix-resource-search"]', 'python');
    fixture.detectChanges();
    expect(service.searchResources).toHaveBeenCalledWith('python', 10, 'ru');

    fixture.nativeElement
      .querySelector<HTMLButtonElement>(`[data-testid="matrix-resource-attach-${RESOURCE_ID}"]`)
      ?.click();
    fixture.detectChanges();
    setTextarea('#matrixResourceContextRu0', 'Читать');
    setTextarea('#matrixResourceContextEn0', 'Read');

    setInput('#matrix-form-slug', 'draft-question');
    selectQuestionSubsection(SUBSECTION_ID);
    setInput('#matrix-form-question-ru', 'Вопрос?');
    setInput('#matrix-form-question-en', 'Question?');
    submitForm();

    expect(emittedPayloads[0].resources).toEqual([
      {
        resourceId: RESOURCE_ID,
        translations: { ru: { context: 'Читать' }, en: { context: 'Read' } },
      },
    ]);
  });

  it('loads existing question values into the edit form', () => {
    fixture.componentRef.setInput('mode', 'edit');
    fixture.componentRef.setInput('question', questionDetail());
    fixture.detectChanges();

    expect(inputValue('#matrix-form-slug')).toBe('existing-question');
    expect(inputValue('#matrix-form-question-en')).toBe('Existing question?');
  });

  function submitForm(): void {
    fixture.debugElement.query(By.css('form')).nativeElement.dispatchEvent(new Event('submit'));
    fixture.detectChanges();
  }

  function setInput(selector: string, value: string): void {
    const input = fixture.nativeElement.querySelector(selector) as HTMLInputElement;
    input.value = value;
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  function setTextarea(selector: string, value: string): void {
    const textarea = fixture.nativeElement.querySelector(selector) as HTMLTextAreaElement;
    textarea.value = value;
    textarea.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  function setMarkdownEditor(selector: string, value: string): void {
    const editor = fixture.debugElement
      .query(By.css(selector))
      ?.query(By.directive(MarkdownEditorStubComponent))?.componentInstance as
      MarkdownEditorStubComponent | undefined;
    if (editor === undefined) {
      throw new Error(`No Markdown editor found for ${selector}`);
    }
    editor.valueChange.emit(value);
    fixture.detectChanges();
  }

  function setSelect(selector: string, value: string): void {
    const select = fixture.nativeElement.querySelector(selector) as HTMLSelectElement;
    select.value = value;
    select.dispatchEvent(new Event('change'));
    fixture.detectChanges();
  }

  function selectQuestionSubsection(subsectionId: string): void {
    const picker = fixture.debugElement.query(By.directive(MatrixStructurePickerStubComponent))
      .componentInstance as MatrixStructurePickerStubComponent;
    picker.selectedSubsectionIdChange.emit(subsectionId);
    fixture.detectChanges();
  }

  function fillValidQuestionMinimum(): void {
    setInput('#matrix-form-slug', 'draft-question');
    selectQuestionSubsection(SUBSECTION_ID);
    setInput('#matrix-form-question-ru', 'Вопрос?');
    setInput('#matrix-form-question-en', 'Question?');
  }

  function clickDisplayMode(mode: 'ru' | 'en' | 'ru-en'): void {
    const button = fixture.nativeElement.querySelector(
      `[data-testid="matrix-form-display-mode-${mode}"]`,
    ) as HTMLButtonElement | null;
    if (button === null) {
      throw new Error(`No display mode button found for ${mode}`);
    }
    button.click();
    fixture.detectChanges();
  }

  function expectInvalidControl(selector: string, expectedMessage: string): void {
    const element = fixture.nativeElement.querySelector(selector) as HTMLElement | null;
    expect(element).not.toBeNull();
    expect(element?.classList).toContain('is-invalid');
    expect(element?.getAttribute('aria-invalid')).toBe('true');
    expect(fixture.nativeElement.textContent).toContain(expectedMessage);
  }

  function inputValue(selector: string): string {
    const input = fixture.nativeElement.querySelector(selector) as HTMLInputElement;
    return input.value;
  }

  function element(selector: string): HTMLElement | null {
    return fixture.nativeElement.querySelector(selector) as HTMLElement | null;
  }

  function selectValue(selector: string): string {
    const select = fixture.nativeElement.querySelector(selector) as HTMLSelectElement;
    return select.value;
  }

  function fieldColumn(selector: string): HTMLElement {
    const field = fixture.nativeElement.querySelector(selector) as HTMLElement | null;
    const column = field?.closest('.row > div, .row > section');
    if (!(column instanceof HTMLElement)) {
      throw new Error(`No grid column found for ${selector}`);
    }
    return column;
  }
});

@Component({
  selector: 'app-matrix-structure-picker',
  standalone: true,
  template:
    '<select data-testid="matrix-structure-subsection" [class.is-invalid]="invalid" [attr.aria-invalid]="invalid ? \'true\' : null"></select>',
})
class MatrixStructurePickerStubComponent {
  @Input({ required: true }) language!: 'ru' | 'en';
  @Input({ required: true }) selectedSubsectionId!: string | null;
  @Input({ required: true }) preferredSheetKey!: string | null;
  @Input() disabled = false;
  @Input() invalid = false;
  @Output() readonly selectedSubsectionIdChange = new EventEmitter<string | null>();
}

@Component({
  selector: 'app-markdown-editor',
  standalone: true,
  template: '',
})
class MarkdownEditorStubComponent {
  @Input({ required: true }) value!: string;
  @Output() readonly valueChange = new EventEmitter<string>();
}

function questionDetail(): AdminMatrixQuestionDetailDto {
  return {
    id: '7',
    slug: 'existing-question',
    question: 'Existing question?',
    answer: '',
    interviewExpectedAnswer: '',
    subsectionId: SUBSECTION_ID,
    sheetKey: 'python',
    sheet: 'Python',
    grade: null,
    interviewFrequency: null,
    section: 'Core',
    subsection: 'Syntax',
    publishStatus: 'Draft',
    translations: {
      ru: { question: 'Существующий вопрос?', answer: '', interviewExpectedAnswer: '' },
      en: { question: 'Existing question?', answer: '', interviewExpectedAnswer: '' },
    },
    resources: [],
  };
}
