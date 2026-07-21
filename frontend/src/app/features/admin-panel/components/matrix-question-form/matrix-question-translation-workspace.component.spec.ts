import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MarkdownEditorComponent } from '../../../../core/editor/markdown-editor.component';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import {
  MatrixQuestionTranslationChange,
  MatrixQuestionTranslationField,
} from './matrix-question-translation.model';
import { MatrixQuestionTranslationWorkspaceComponent } from './matrix-question-translation-workspace.component';

const initialFields: readonly MatrixQuestionTranslationField[] = [
  {
    scope: 'question',
    fieldId: 'question',
    source: 'Что такое Protocol?',
    translation: 'Что такое Protocol?',
    editable: true,
    required: true,
    maxLength: 255,
  },
  {
    scope: 'question',
    fieldId: 'answer',
    source: 'Используйте `Protocol`.',
    translation: '',
    editable: true,
    required: true,
    maxLength: 20_000,
  },
  {
    scope: 'question',
    fieldId: 'interviewAnswerExplanation',
    source: 'Проверяет типизацию.',
    translation: 'Checks typing knowledge.',
    editable: true,
    required: true,
    maxLength: 20_000,
  },
  {
    scope: 'resource',
    resourceId: 'resource-1',
    fieldId: 'name',
    resourceLabel: 'Документация Python',
    resourceUrl: 'https://docs.python.org',
    source: 'Python',
    translation: 'Python',
    editable: false,
    required: false,
    maxLength: 255,
  },
  {
    scope: 'resource',
    resourceId: 'new--1',
    fieldId: 'name',
    resourceLabel: 'Новый ресурс',
    resourceUrl: 'https://example.com',
    source: 'Новый ресурс',
    translation: 'New resource',
    editable: true,
    required: true,
    maxLength: 255,
  },
  {
    scope: 'resource',
    resourceId: 'new--1',
    fieldId: 'context',
    resourceLabel: 'Новый ресурс',
    resourceUrl: 'https://example.com',
    source: '',
    translation: '',
    editable: true,
    required: false,
    maxLength: 20_000,
  },
];

describe('MatrixQuestionTranslationWorkspaceComponent', () => {
  let fixture: ComponentFixture<MatrixQuestionTranslationWorkspaceComponent>;
  let notifications: jest.Mocked<Pick<NotificationService, 'success' | 'error'>>;
  let clipboardDescriptor: PropertyDescriptor | undefined;

  beforeEach(async () => {
    clipboardDescriptor = Object.getOwnPropertyDescriptor(window.navigator, 'clipboard');
    notifications = {
      success: jest.fn(),
      error: jest.fn(),
    };
    await TestBed.configureTestingModule({
      imports: [MatrixQuestionTranslationWorkspaceComponent],
      providers: [provideI18nTesting(), { provide: NotificationService, useValue: notifications }],
    })
      .overrideComponent(MatrixQuestionTranslationWorkspaceComponent, {
        remove: { imports: [MarkdownEditorComponent] },
        add: { imports: [MarkdownEditorStubComponent] },
      })
      .compileComponents();

    fixture = TestBed.createComponent(MatrixQuestionTranslationWorkspaceComponent);
    fixture.componentRef.setInput('fields', initialFields);
    fixture.componentRef.setInput('resetKey', 'question:1');
    fixture.componentRef.setInput('disabled', false);
    fixture.detectChanges();
  });

  afterEach(() => {
    Object.defineProperty(window.navigator, 'clipboard', {
      configurable: true,
      ...(clipboardDescriptor ?? { value: undefined }),
    });
  });

  it('renders connected responsive pairs and counts translation completeness independently', () => {
    const pairs = fixture.nativeElement.querySelectorAll<HTMLElement>(
      '[data-testid="matrix-translation-field"]',
    );
    const sourceColumn = fixture.nativeElement.querySelector<HTMLElement>(
      '.matrix-translation-source-column',
    );
    const existingResourceName = fixture.nativeElement.querySelector<HTMLInputElement>(
      '[data-testid="matrix-translation-target-resource-resource-1-name"]',
    );
    const newResourceName = fixture.nativeElement.querySelector<HTMLInputElement>(
      '[data-testid="matrix-translation-target-resource-new--1-name"]',
    );
    const sourceValues = Array.from(
      fixture.nativeElement.querySelectorAll<HTMLElement>(
        '[data-testid^="matrix-translation-source-"]',
      ),
    );

    expect(pairs).toHaveLength(initialFields.length);
    expect(pairs[0].classList).toContain('matrix-translation-field-card');
    expect(sourceColumn?.classList).toContain('col-lg-6');
    expect(sourceValues).toHaveLength(initialFields.length);
    expect(sourceValues.every((source) => source.tagName === 'DIV')).toBe(true);
    expect(sourceValues.every((source) => source.tabIndex === -1)).toBe(true);
    expect(sourceValues[0].textContent).toBe(initialFields[0].source);
    expect(existingResourceName?.readOnly).toBe(true);
    expect(newResourceName?.readOnly).toBe(false);
    expect(text('[data-testid="matrix-translation-completeness"]')).toContain('2 / 4');
    expect(status('question:question')).toBe('identical');
    expect(status('resource:new--1:context')).toBe('notApplicable');
  });

  it('requires explicit review for identical text and resets it after either side changes', () => {
    click('[data-testid="matrix-translation-review-question-question"]');

    expect(status('question:question')).toBe('reviewed');
    expect(text('[data-testid="matrix-translation-completeness"]')).toContain('3 / 4');

    fixture.componentRef.setInput(
      'fields',
      initialFields.map((field) =>
        field.scope === 'question' && field.fieldId === 'question'
          ? { ...field, source: 'Что такое PEP 8?', translation: 'Что такое PEP 8?' }
          : field,
      ),
    );
    fixture.detectChanges();

    expect(status('question:question')).toBe('identical');
    expect(text('[data-testid="matrix-translation-completeness"]')).toContain('2 / 4');
  });

  it('keeps review through view persistence updates and clears it for another question', () => {
    click('[data-testid="matrix-translation-review-question-question"]');
    fixture.componentRef.setInput('fields', [...initialFields]);
    fixture.detectChanges();
    expect(status('question:question')).toBe('reviewed');

    fixture.componentRef.setInput('resetKey', 'question:2');
    fixture.detectChanges();
    expect(status('question:question')).toBe('identical');
  });

  it('reports clipboard success, unavailable source/API, and rejected writes', async () => {
    const writeText = jest.fn().mockResolvedValue(undefined);
    setClipboard({ writeText });

    fixture.componentInstance.copySource(initialFields[0]);
    await fixture.whenStable();
    expect(writeText).toHaveBeenCalledWith('Что такое Protocol?');
    expect(notifications.success).toHaveBeenCalledWith('Текст скопирован.');

    fixture.componentInstance.copySource(initialFields[5]);
    expect(notifications.error).toHaveBeenCalledWith('В этом поле нет RU-текста для копирования.');

    setClipboard(undefined);
    fixture.componentInstance.copySource(initialFields[0]);
    expect(notifications.error).toHaveBeenCalledWith('Буфер обмена недоступен в этом браузере.');

    setClipboard({ writeText: jest.fn().mockRejectedValue(new Error('Denied')) });
    fixture.componentInstance.copySource(initialFields[0]);
    await fixture.whenStable();
    expect(notifications.error).toHaveBeenCalledWith('Не удалось скопировать текст.');
  });

  it('copies a complete versioned package with raw source and current translations', async () => {
    const writeText = jest.fn().mockResolvedValue(undefined);
    setClipboard({ writeText });

    fixture.componentInstance.copyAll();
    await fixture.whenStable();

    const copied = JSON.parse(writeText.mock.calls[0][0] as string) as {
      schema: string;
      fields: { source: string; translation: string; editable: boolean }[];
    };
    expect(copied.schema).toBe('matrix-question-translation');
    expect(copied.fields).toHaveLength(initialFields.length);
    expect(copied.fields[1]).toEqual(
      expect.objectContaining({ source: 'Используйте `Protocol`.', translation: '' }),
    );
    expect(copied.fields[3].editable).toBe(false);
  });

  it('previews partial imports and applies only selected valid changed rows', () => {
    const changes: MatrixQuestionTranslationChange[] = [];
    fixture.componentInstance.translationChange.subscribe((change) => changes.push(change));
    setImportValue(
      JSON.stringify({
        schema: 'matrix-question-translation',
        version: 1,
        sourceLanguage: 'ru',
        targetLanguage: 'en',
        task: 'translate',
        fields: [
          packageField(initialFields[0], 'What is Protocol?'),
          packageField(initialFields[3], 'Python docs'),
          packageField(initialFields[4], 'New documentation resource'),
        ],
      }),
    );
    click('[data-testid="matrix-translation-import-preview"]');

    expect(
      fixture.nativeElement.querySelectorAll('[data-testid="matrix-translation-preview-row"]'),
    ).toHaveLength(3);
    expect(previewStatus('question:question')).toBe('changed');
    expect(previewStatus('resource:resource-1:name')).toBe('readOnly');
    const newNameCheckbox = fixture.nativeElement.querySelector<HTMLInputElement>(
      '[data-testid="matrix-translation-preview-select-resource:new--1:name"]',
    );
    expect(newNameCheckbox?.checked).toBe(true);
    newNameCheckbox?.click();
    fixture.detectChanges();

    click('[data-testid="matrix-translation-import-apply"]');

    expect(changes).toEqual([
      {
        scope: 'question',
        fieldId: 'question',
        value: 'What is Protocol?',
      },
    ]);
    expect(notifications.success).toHaveBeenCalledWith('Применено полей: 1.');
  });

  it('shows an inline error for an invalid package and emits direct EN preview requests', () => {
    setImportValue('not json');
    click('[data-testid="matrix-translation-import-preview"]');
    expect(text('[data-testid="matrix-translation-import-error"]')).toContain(
      'Не удалось прочитать JSON.',
    );

    const previewEnglish = jest.fn();
    fixture.componentInstance.previewEnglish.subscribe(previewEnglish);
    click('[data-testid="matrix-translation-preview-en"]');
    expect(previewEnglish).toHaveBeenCalledTimes(1);
  });

  function click(selector: string): void {
    fixture.nativeElement.querySelector<HTMLButtonElement>(selector)?.click();
    fixture.detectChanges();
  }

  function text(selector: string): string {
    return fixture.nativeElement.querySelector<HTMLElement>(selector)?.textContent?.trim() ?? '';
  }

  function status(key: string): string | null | undefined {
    return fixture.nativeElement
      .querySelector<HTMLElement>(`[data-translation-key="${key}"]`)
      ?.getAttribute('data-translation-status');
  }

  function previewStatus(key: string): string | null | undefined {
    return fixture.nativeElement
      .querySelector<HTMLElement>(
        `[data-testid="matrix-translation-preview-row"][data-translation-key="${key}"]`,
      )
      ?.getAttribute('data-preview-status');
  }

  function setImportValue(value: string): void {
    const textarea = fixture.nativeElement.querySelector<HTMLTextAreaElement>(
      '[data-testid="matrix-translation-import-input"]',
    );
    if (textarea === null) throw new Error('No translation package input');
    textarea.value = value;
    textarea.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  function setClipboard(clipboard: Pick<Clipboard, 'writeText'> | undefined): void {
    Object.defineProperty(window.navigator, 'clipboard', {
      configurable: true,
      value: clipboard,
    });
  }
});

function packageField(
  field: MatrixQuestionTranslationField,
  translation: string,
): Record<string, unknown> {
  return {
    scope: field.scope,
    ...(field.scope === 'resource' ? { resourceId: field.resourceId } : {}),
    fieldId: field.fieldId,
    source: field.source,
    translation,
    editable: field.editable,
  };
}

@Component({ selector: 'app-markdown-editor', standalone: true, template: '' })
class MarkdownEditorStubComponent {
  @Input({ required: true }) value!: string;
  @Output() readonly valueChange = new EventEmitter<string>();
}
