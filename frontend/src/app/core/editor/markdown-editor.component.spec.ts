import { CSP_NONCE, PLATFORM_ID } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EditorView } from '@codemirror/view';
import { of, throwError } from 'rxjs';
import { provideI18nTesting } from '../../testing/i18n-testing';
import { EditorImageUploadService } from './editor-image-upload.service';
import { MarkdownEditorComponent } from './markdown-editor.component';

const EDITOR_MESSAGES = {
  'markdownEditor.mode.aria': 'Режим Markdown-редактора',
  'markdownEditor.mode.edit': 'Редактор',
  'markdownEditor.mode.preview': 'Превью',
  'markdownEditor.preview.empty': 'Нет содержимого для предпросмотра.',
  'markdownEditor.shortcuts.summary': 'Горячие клавиши',
  'markdownEditor.shortcuts.tabEscape': 'Нажмите Escape, затем Tab, чтобы выйти из редактора.',
  'markdownEditor.shortcuts.modifierHintMac': 'Основная клавиша на macOS — ⌘.',
  'markdownEditor.shortcuts.modifierHintOther': 'Основная клавиша на Windows и Linux — Ctrl.',
  'markdownEditor.shortcuts.group.view': 'Навигация',
  'markdownEditor.shortcuts.group.headings': 'Заголовки',
  'markdownEditor.shortcuts.group.inline': 'Текст и ссылки',
  'markdownEditor.shortcuts.group.blocks': 'Блоки',
  'markdownEditor.shortcuts.group.media': 'Медиа',
  'markdownEditor.upload.uploading': 'Загрузка изображения…',
  'markdownEditor.upload.failed': 'Не удалось загрузить {fileName}.',
  'markdownEditor.upload.retry': 'Повторить',
  'markdownEditor.upload.dismiss': 'Закрыть',
  'markdownEditor.search.find': 'Найти',
  'markdownEditor.search.replace': 'Заменить',
  'markdownEditor.search.next': 'Следующее',
  'markdownEditor.search.previous': 'Предыдущее',
  'markdownEditor.search.all': 'Все',
  'markdownEditor.search.matchCase': 'Учитывать регистр',
  'markdownEditor.search.byWord': 'Слово целиком',
  'markdownEditor.search.close': 'Закрыть',
};

describe('MarkdownEditorComponent', () => {
  let fixture: ComponentFixture<MarkdownEditorComponent>;
  let uploadService: { uploadEditorImage: jest.Mock };

  beforeEach(async () => {
    uploadService = {
      uploadEditorImage: jest.fn().mockReturnValue(of('https://cdn.example.com/image.png')),
    };

    await TestBed.configureTestingModule({
      imports: [MarkdownEditorComponent],
      providers: [
        { provide: CSP_NONCE, useValue: 'markdown-editor-test-nonce' },
        { provide: EditorImageUploadService, useValue: uploadService },
        provideI18nTesting(EDITOR_MESSAGES),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MarkdownEditorComponent);
    fixture.componentRef.setInput('value', 'Initial **markdown**');
    fixture.componentRef.setInput('language', 'ru');
    fixture.componentRef.setInput('accessibleLabel', 'Содержимое статьи RU');
    fixture.detectChanges();
  });

  afterEach(() => fixture.destroy());

  it('creates a CodeMirror Markdown source editor without taking focus', () => {
    const editor = editorElement();

    expect(editor).not.toBeNull();
    expect(editor.textContent).toContain('Initial **markdown**');
    expect(contentElement().getAttribute('aria-label')).toBe('Содержимое статьи RU');
    expect(contentElement().getAttribute('lang')).toBe('ru');
    expect(contentElement().getAttribute('spellcheck')).toBe('true');
    expect(document.activeElement).not.toBe(contentElement());
    expect(fixture.nativeElement.querySelector('.toastui-editor-defaultUI')).toBeNull();
  });

  it('exposes a CSP-safe theme hook with line numbers and forced wrapping', () => {
    const editor = editorElement();
    const announcement = query<HTMLElement>('.cm-announced');
    const lineNumbers = Array.from(
      fixture.nativeElement.querySelectorAll<HTMLElement>('.cm-lineNumbers .cm-gutterElement'),
    )
      .map((element) => element.textContent?.trim())
      .filter(Boolean);

    expect(editor.classList).toContain('markdown-editor-static-theme');
    expect(lineNumbers).toContain('1');
    expect(contentElement().classList).toContain('cm-lineWrapping');
    expect(announcement.getAttribute('aria-live')).toBe('polite');
  });

  it('passes the Angular CSP nonce to CodeMirror runtime styles', () => {
    const editorView = EditorView.findFromDOM(contentElement());
    const runtimeStyles = Array.from(document.head.querySelectorAll('style')).filter((style) =>
      style.textContent?.includes('.cm-content'),
    );

    expect(editorView?.state.facet(EditorView.cspNonce)).toBe('markdown-editor-test-nonce');
    expect(
      runtimeStyles.some((style) => style.getAttribute('nonce') === 'markdown-editor-test-nonce'),
    ).toBe(true);
  });

  it('adds readable semi-rendering classes for Markdown structure and inline code', () => {
    fixture.componentRef.setInput(
      'value',
      [
        '# Heading one',
        '## Heading two',
        '> Quote',
        '> [!NOTE] Callout',
        '- List item',
        '- [ ] Task item',
        '`inline code`',
        '```python',
        'def answer(value):',
        '    return value + 25',
        '```',
        '| Name | Value |',
        '| --- | --- |',
        '| Answer | 25 |',
        '',
        '---',
      ].join('\n'),
    );
    fixture.detectChanges();
    const lines = Array.from(fixture.nativeElement.querySelectorAll<HTMLElement>('.cm-line'));
    const lineContaining = (text: string): HTMLElement => {
      const line = lines.find((candidate) => candidate.textContent?.includes(text));
      expect(line).toBeDefined();
      return line as HTMLElement;
    };

    expect(lineContaining('# Heading one').classList).toContain('cm-markdown-heading-1');
    expect(lineContaining('## Heading two').classList).toContain('cm-markdown-heading-2');
    expect(lineContaining('> Quote').classList).toContain('cm-markdown-quote');
    expect(lineContaining('[!NOTE]').classList).toContain('cm-markdown-callout');
    expect(lineContaining('- List item').classList).toContain('cm-markdown-list');
    expect(lineContaining('[ ] Task item').classList).toContain('cm-markdown-task');
    expect(lineContaining('```python').classList).toContain('cm-markdown-code-fence');
    expect(lineContaining('def answer').classList).toContain('cm-markdown-code-block');
    expect(lineContaining('return value').classList).toContain('cm-markdown-code-block');
    expect(lineContaining('| Name | Value |').classList).toContain('cm-markdown-table');
    expect(lineContaining('| --- | --- |').classList).toContain('cm-markdown-table');
    expect(lineContaining('| Answer | 25 |').classList).toContain('cm-markdown-table');
    expect(lines.find((line) => line.textContent === '---')?.classList).toContain(
      'cm-markdown-horizontal-rule',
    );
    expect(query<HTMLElement>('.cm-markdown-inline-code').textContent).toContain('inline code');
    const codeKeyword = query<HTMLElement>('.cm-prism-keyword');
    expect(codeKeyword.textContent).toMatch(/def|return/);
    expect(codeKeyword.classList).toContain('tok-keyword');
    expect(query<HTMLElement>('.cm-prism-function').textContent).toBe('answer');
    expect(query<HTMLElement>('.cm-prism-number').textContent).toBe('25');
    expect(fixture.nativeElement.querySelector('.tok-heading')).not.toBeNull();
  });

  it('focuses the source editor through the public wrapper API', () => {
    fixture.componentInstance.focus();

    expect(document.activeElement).toBe(contentElement());
  });

  it('updates content language and accessible name without rebuilding CodeMirror', () => {
    const editor = editorElement();

    fixture.componentRef.setInput('language', 'en');
    fixture.componentRef.setInput('accessibleLabel', 'Article content EN');
    fixture.detectChanges();

    expect(editorElement()).toBe(editor);
    expect(contentElement().getAttribute('lang')).toBe('en');
    expect(contentElement().getAttribute('aria-label')).toBe('Article content EN');
  });

  it('switches between accessible source and preview tabs and restores editor focus', () => {
    const previewTab = query<HTMLButtonElement>('[data-testid="markdown-editor-preview-tab"]');
    previewTab.click();
    fixture.detectChanges();

    expect(previewTab.getAttribute('aria-selected')).toBe('true');
    expect(query<HTMLElement>('[data-testid="markdown-editor-preview-panel"]').hidden).toBe(false);
    expect(query<HTMLElement>('[data-testid="markdown-editor-source-panel"]').hidden).toBe(true);

    fixture.componentInstance.focus();
    fixture.detectChanges();

    expect(query<HTMLElement>('[data-testid="markdown-editor-source-panel"]').hidden).toBe(false);
    expect(document.activeElement).toBe(contentElement());
  });

  it('supports keyboard navigation between the mode tabs', () => {
    const editTab = query<HTMLButtonElement>('[data-testid="markdown-editor-edit-tab"]');
    const previewTab = query<HTMLButtonElement>('[data-testid="markdown-editor-preview-tab"]');
    editTab.focus();

    editTab.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));

    expect(document.activeElement).toBe(previewTab);
  });

  it('renders unsaved Markdown through the sanitized centralized preview', () => {
    const warning = jest.spyOn(console, 'warn').mockImplementation(() => undefined);
    fixture.componentRef.setInput(
      'value',
      [
        '**Safe** [[articles:example|Article]]',
        '```ts',
        'const answer = 42;',
        '```',
        '<script>alert("script")</script>',
        '<img src="x" onerror="alert(2)">',
      ].join('\n'),
    );
    fixture.detectChanges();
    query<HTMLButtonElement>('[data-testid="markdown-editor-preview-tab"]').click();
    fixture.detectChanges();

    const preview = query<HTMLElement>('[data-testid="markdown-editor-preview-content"]');
    expect(preview.querySelector('strong')?.textContent).toBe('Safe');
    expect(preview.querySelector('a')?.getAttribute('href')).toBe('/ru/articles/example');
    expect(preview.querySelector('code .token.keyword')?.textContent).toBe('const');
    expect(preview.innerHTML).not.toContain('<script');
    expect(preview.innerHTML).not.toContain('onerror');
    warning.mockRestore();
  });

  it('emits physical-key formatting commands on a non-English keyboard layout', () => {
    const emitted: string[] = [];
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'KeyB',
        key: 'и',
        ctrlKey: true,
      }),
    );
    fixture.detectChanges();

    expect(emitted.at(-1)).toBe('****Initial **markdown**');
  });

  it('toggles preview with the physical Mod+E shortcut', () => {
    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'KeyE',
        key: 'у',
        ctrlKey: true,
      }),
    );
    fixture.detectChanges();

    expect(query<HTMLElement>('[data-testid="markdown-editor-preview-panel"]').hidden).toBe(false);
  });

  it('restores editor focus and scroll after toggling preview from the keyboard', () => {
    const scroller = query<HTMLElement>('.cm-scroller');
    scroller.scrollTop = 84;
    contentElement().focus();

    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'KeyE',
        key: 'e',
        ctrlKey: true,
      }),
    );
    fixture.detectChanges();
    expect(document.activeElement).toBe(
      query<HTMLButtonElement>('[data-testid="markdown-editor-preview-tab"]'),
    );
    document.activeElement?.dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'KeyE',
        key: 'e',
        ctrlKey: true,
      }),
    );
    fixture.detectChanges();

    expect(scroller.scrollTop).toBe(84);
    expect(document.activeElement).toBe(contentElement());
  });

  it('opens localized CodeMirror search and contains editor shortcuts inside the editor', () => {
    const outerListener = jest.fn();
    fixture.nativeElement.addEventListener('keydown', outerListener);
    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'KeyF',
        key: 'а',
        ctrlKey: true,
      }),
    );
    fixture.detectChanges();

    expect(query<HTMLInputElement>('.cm-search input[name="search"]').placeholder).toBe('Найти');
    expect(outerListener).not.toHaveBeenCalled();
  });

  it('suppresses matching shortcuts during IME composition without changing content', () => {
    const emitted: string[] = [];
    const outerListener = jest.fn();
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    fixture.nativeElement.addEventListener('keydown', outerListener);

    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'KeyB',
        key: 'и',
        ctrlKey: true,
        isComposing: true,
      }),
    );

    expect(emitted).toEqual([]);
    expect(outerListener).not.toHaveBeenCalled();
  });

  it('does not emit when an external value update is synchronized', () => {
    const emitted: string[] = [];
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));

    fixture.componentRef.setInput('value', 'Externally updated');
    fixture.detectChanges();

    expect(editorElement().textContent).toContain('Externally updated');
    expect(emitted).toEqual([]);
  });

  it('uploads pasted images and inserts their Markdown in stable order', () => {
    const emitted: string[] = [];
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    uploadService.uploadEditorImage.mockImplementation((file: File) =>
      of(`https://cdn.example.com/${file.name}`),
    );

    contentElement().dispatchEvent(
      pasteEvent([
        new File(['first'], 'first.png', { type: 'image/png' }),
        new File(['second'], 'second.png', { type: 'image/png' }),
      ]),
    );
    fixture.detectChanges();

    expect(uploadService.uploadEditorImage).toHaveBeenCalledTimes(2);
    expect(emitted.at(-1)).toBe(
      '![first.png](https://cdn.example.com/first.png)' +
        '![second.png](https://cdn.example.com/second.png)' +
        'Initial **markdown**',
    );
  });

  it('uploads images selected through the hidden multi-file picker', () => {
    const emitted: string[] = [];
    const file = new File(['picked'], 'picked image.png', { type: 'image/png' });
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    uploadService.uploadEditorImage.mockReturnValue(of('https://cdn.example.com/picked.png'));
    const input = query<HTMLInputElement>('input[type="file"]');
    Object.defineProperty(input, 'files', { configurable: true, value: [file] });

    input.dispatchEvent(new Event('change', { bubbles: true }));
    fixture.detectChanges();

    expect(uploadService.uploadEditorImage).toHaveBeenCalledWith(file);
    expect(emitted.at(-1)).toBe(
      '![picked image.png](https://cdn.example.com/picked.png)Initial **markdown**',
    );
  });

  it('uploads dropped images at the editor selection', () => {
    const emitted: string[] = [];
    const file = new File(['dropped'], 'dropped.png', { type: 'image/png' });
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    uploadService.uploadEditorImage.mockReturnValue(of('https://cdn.example.com/dropped.png'));
    const position = jest.spyOn(EditorView.prototype, 'posAtCoords').mockReturnValue(null);

    contentElement().dispatchEvent(dropEvent([file]));
    fixture.detectChanges();

    expect(uploadService.uploadEditorImage).toHaveBeenCalledWith(file);
    expect(emitted.at(-1)).toBe(
      '![dropped.png](https://cdn.example.com/dropped.png)Initial **markdown**',
    );
    position.mockRestore();
  });

  it('keeps content unchanged on upload failure and supports retry', () => {
    const emitted: string[] = [];
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    uploadService.uploadEditorImage
      .mockReturnValueOnce(throwError(() => new Error('upload failed')))
      .mockReturnValueOnce(of('https://cdn.example.com/retried.png'));

    contentElement().dispatchEvent(
      pasteEvent([new File(['image'], 'retry.png', { type: 'image/png' })]),
    );
    fixture.detectChanges();

    expect(emitted).toEqual([]);
    expect(
      query<HTMLElement>('[data-testid="markdown-editor-upload-error"]').textContent,
    ).toContain('retry.png');

    query<HTMLButtonElement>('[data-testid="markdown-editor-upload-retry"]').click();
    fixture.detectChanges();

    expect(emitted.at(-1)).toBe(
      '![retry.png](https://cdn.example.com/retried.png)Initial **markdown**',
    );
  });

  it('dismisses a failed upload without changing the editor text', () => {
    const emitted: string[] = [];
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    uploadService.uploadEditorImage.mockReturnValue(throwError(() => new Error('upload failed')));
    contentElement().dispatchEvent(
      pasteEvent([new File(['image'], 'dismiss.png', { type: 'image/png' })]),
    );
    fixture.detectChanges();

    query<HTMLButtonElement>('[data-testid="markdown-editor-upload-dismiss"]').click();
    fixture.detectChanges();

    expect(emitted).toEqual([]);
    expect(
      fixture.nativeElement.querySelector('[data-testid="markdown-editor-upload-error"]'),
    ).toBeNull();
  });

  it('lets Escape followed by Tab leave CodeMirror without a keyboard trap', () => {
    const content = contentElement();
    content.focus();
    content.dispatchEvent(
      keyboardEventWithKeyCode(
        {
          bubbles: true,
          cancelable: true,
          code: 'Escape',
          key: 'Escape',
        },
        27,
      ),
    );
    const tab = keyboardEventWithKeyCode(
      {
        bubbles: true,
        cancelable: true,
        code: 'Tab',
        key: 'Tab',
      },
      9,
    );

    content.dispatchEvent(tab);

    expect(tab.defaultPrevented).toBe(false);
  });

  it('documents the keyboard escape hatch beside the shortcut reference', () => {
    const shortcuts = query<HTMLElement>('[data-testid="markdown-editor-shortcuts"]');

    expect(shortcuts.textContent).toContain('Escape');
    expect(shortcuts.textContent).toContain('Tab');
    expect(shortcuts.textContent).toContain('Ctrl');
    expect(shortcuts.textContent).toContain('B');
  });

  it('groups shortcuts into readable cards and expands Mod to the actual platform key', () => {
    const shortcuts = query<HTMLElement>('[data-testid="markdown-editor-shortcuts"]');
    shortcuts.querySelector('summary')?.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    fixture.detectChanges();
    const groups = shortcuts.querySelectorAll('[data-testid="markdown-editor-shortcut-group"]');

    expect(groups).toHaveLength(5);
    expect(shortcuts.textContent).toContain('Навигация');
    expect(shortcuts.textContent).toContain('Текст и ссылки');
    expect(shortcuts.textContent).toContain('Ctrl');
    expect(shortcuts.textContent).not.toContain('Mod+');
    expect(shortcuts.querySelectorAll('.markdown-editor-keycap').length).toBeGreaterThan(20);
  });

  function editorElement(): HTMLElement {
    return query<HTMLElement>('.cm-editor');
  }

  function contentElement(): HTMLElement {
    return query<HTMLElement>('.cm-content');
  }

  function query<T extends Element>(selector: string): T {
    const element = fixture.nativeElement.querySelector(selector) as T | null;
    if (element === null) {
      throw new Error(`Missing element: ${selector}`);
    }
    return element;
  }
});

describe('MarkdownEditorComponent on the server', () => {
  it('does not initialize CodeMirror or access browser-only editor APIs', async () => {
    await TestBed.configureTestingModule({
      imports: [MarkdownEditorComponent],
      providers: [
        { provide: PLATFORM_ID, useValue: 'server' },
        {
          provide: EditorImageUploadService,
          useValue: { uploadEditorImage: jest.fn() },
        },
        provideI18nTesting(EDITOR_MESSAGES),
      ],
    }).compileComponents();
    const fixture = TestBed.createComponent(MarkdownEditorComponent);
    fixture.componentRef.setInput('value', 'Server Markdown');
    fixture.componentRef.setInput('language', 'en');
    fixture.componentRef.setInput('accessibleLabel', 'Article content');

    expect(() => fixture.detectChanges()).not.toThrow();
    expect(fixture.nativeElement.querySelector('.cm-editor')).toBeNull();
    fixture.destroy();
  });
});

function pasteEvent(files: readonly File[]): Event {
  const event = new Event('paste', { bubbles: true, cancelable: true });
  Object.defineProperty(event, 'clipboardData', {
    value: {
      items: files.map((file) => ({
        kind: 'file',
        type: file.type,
        getAsFile: () => file,
      })),
    },
  });
  return event;
}

function dropEvent(files: readonly File[]): Event {
  const event = new Event('drop', { bubbles: true, cancelable: true });
  Object.defineProperty(event, 'dataTransfer', {
    value: {
      files,
      items: files.map((file) => ({ kind: 'file', type: file.type })),
    },
  });
  return event;
}

function keyboardEventWithKeyCode(init: KeyboardEventInit, keyCode: number): KeyboardEvent {
  const event = new KeyboardEvent('keydown', init);
  Object.defineProperty(event, 'keyCode', { value: keyCode });
  return event;
}
