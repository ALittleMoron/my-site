import { CdkTrapFocus } from '@angular/cdk/a11y';
import { CSP_NONCE, PLATFORM_ID } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { CompletionContext } from '@codemirror/autocomplete';
import { undo } from '@codemirror/commands';
import { EditorSelection } from '@codemirror/state';
import { EditorView } from '@codemirror/view';
import { of, throwError } from 'rxjs';
import { provideI18nTesting } from '../../testing/i18n-testing';
import { ModalPageScrollLockService } from '../layout/modal-page-scroll-lock.service';
import { WikiLinkTargetsService } from '../wiki-links/wiki-link-targets.service';
import { createWikiLinkTargetRegistry } from '../wiki-links/wiki-links';
import { EditorImageUploadService } from './editor-image-upload.service';
import { MARKDOWN_EDITOR_SHORTCUT_GROUPS } from './markdown-editor.commands';
import { MarkdownEditorComponent } from './markdown-editor.component';
import { wikiLinkCompletionSource } from './markdown-editor.wiki-links';

const EDITOR_MESSAGES = {
  'markdownEditor.mode.aria': 'Режим Markdown-редактора',
  'markdownEditor.mode.edit': 'Редактор',
  'markdownEditor.mode.preview': 'Превью',
  'markdownEditor.fullscreen.enter': 'Развернуть редактор на весь экран',
  'markdownEditor.fullscreen.exit': 'Выйти из полноэкранного режима',
  'markdownEditor.toolbar.aria': 'Действия Markdown-редактора',
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
  'markdownEditor.completions': 'Варианты',
  'markdownEditor.wikiLinks.registryUnavailable': 'Не удалось загрузить варианты wiki-ссылок.',
  'markdownEditor.command.togglePreview': 'Редактор / Превью',
  'markdownEditor.command.heading1': 'Заголовок 1',
  'markdownEditor.command.heading2': 'Заголовок 2',
  'markdownEditor.command.heading3': 'Заголовок 3',
  'markdownEditor.command.heading4': 'Заголовок 4',
  'markdownEditor.command.heading5': 'Заголовок 5',
  'markdownEditor.command.heading6': 'Заголовок 6',
  'markdownEditor.command.bold': 'Жирный',
  'markdownEditor.command.italic': 'Курсив',
  'markdownEditor.command.strikethrough': 'Зачёркнутый',
  'markdownEditor.command.quote': 'Цитата',
  'markdownEditor.command.unorderedList': 'Маркированный список',
  'markdownEditor.command.orderedList': 'Нумерованный список',
  'markdownEditor.command.taskList': 'Список задач',
  'markdownEditor.command.horizontalRule': 'Горизонтальная линия',
  'markdownEditor.command.link': 'Ссылка',
  'markdownEditor.command.image': 'Изображение',
  'markdownEditor.command.inlineCode': 'Строчный код',
  'markdownEditor.command.codeBlock': 'Блок кода',
  'markdownEditor.command.table': 'Таблица',
  'markdownEditor.command.search': 'Поиск и замена',
  'enum.publishStatus.Draft': 'Черновик',
  'enum.publishStatus.Published': 'Опубликовано',
};

const RU_WIKI_LINK_REGISTRY = createWikiLinkTargetRegistry([
  { type: 'articles', items: [] },
  {
    type: 'matrix',
    items: [
      {
        slug: 'known-question',
        title: 'Известный вопрос',
        publishStatus: 'Draft',
      },
    ],
  },
]);

const EN_WIKI_LINK_REGISTRY = createWikiLinkTargetRegistry([
  { type: 'articles', items: [] },
  {
    type: 'matrix',
    items: [
      {
        slug: 'known-question',
        title: 'Known question',
        publishStatus: 'Draft',
      },
    ],
  },
]);

describe('MarkdownEditorComponent', () => {
  let fixture: ComponentFixture<MarkdownEditorComponent>;
  let uploadService: { uploadEditorImage: jest.Mock };
  let wikiLinkTargetsService: { getTargets: jest.Mock };
  let acquirePageScrollLock: jest.Mock;
  let releasePageScrollLock: jest.Mock;

  beforeEach(async () => {
    Object.defineProperty(Range.prototype, 'getClientRects', {
      configurable: true,
      value: () => [],
    });
    uploadService = {
      uploadEditorImage: jest.fn().mockReturnValue(of('https://cdn.example.com/image.png')),
    };
    wikiLinkTargetsService = {
      getTargets: jest
        .fn()
        .mockImplementation((language: string) =>
          of(language === 'ru' ? RU_WIKI_LINK_REGISTRY : EN_WIKI_LINK_REGISTRY),
        ),
    };
    releasePageScrollLock = jest.fn();
    acquirePageScrollLock = jest.fn(() => releasePageScrollLock);

    await TestBed.configureTestingModule({
      imports: [MarkdownEditorComponent],
      providers: [
        { provide: CSP_NONCE, useValue: 'markdown-editor-test-nonce' },
        { provide: EditorImageUploadService, useValue: uploadService },
        {
          provide: ModalPageScrollLockService,
          useValue: { acquire: acquirePageScrollLock },
        },
        { provide: WikiLinkTargetsService, useValue: wikiLinkTargetsService },
        provideI18nTesting(EDITOR_MESSAGES),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MarkdownEditorComponent);
    fixture.componentRef.setInput('value', 'Initial **markdown**');
    fixture.componentRef.setInput('language', 'ru');
    fixture.componentRef.setInput('accessibleLabel', 'Содержимое статьи RU');
    fixture.componentRef.setInput('imageUploadsEnabled', true);
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

  it('removes every image-upload entry point when uploads are disabled', () => {
    fixture.componentRef.setInput('imageUploadsEnabled', false);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-markdown-command="image"]')).toBeNull();
    expect(fixture.nativeElement.querySelector('input[type="file"]')).toBeNull();

    contentElement().dispatchEvent(
      pasteEvent([new File(['image'], 'private.png', { type: 'image/png' })]),
    );

    expect(uploadService.uploadEditorImage).not.toHaveBeenCalled();
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

  it('moves the cursor to the document end when the empty area below the last line is clicked', () => {
    const view = editorView();
    view.dispatch({ selection: { anchor: 0 } });
    jest.spyOn(view, 'coordsAtPos').mockReturnValue({
      left: 16,
      right: 16,
      top: 24,
      bottom: 48,
    });

    const event = new MouseEvent('mousedown', {
      bubbles: true,
      cancelable: true,
      button: 0,
      clientX: 80,
      clientY: 160,
    });
    contentElement().dispatchEvent(event);

    expect(view.state.selection.main.anchor).toBe(view.state.doc.length);
    expect(document.activeElement).toBe(contentElement());
    expect(event.defaultPrevented).toBe(true);
  });

  it('moves the cursor to the document end when the fullscreen area below the content is clicked', () => {
    query<HTMLButtonElement>('[data-testid="markdown-editor-fullscreen-toggle"]').click();
    fixture.detectChanges();
    const view = editorView();
    view.dispatch({ selection: { anchor: 0 } });
    jest.spyOn(view, 'coordsAtPos').mockReturnValue({
      left: 16,
      right: 16,
      top: 24,
      bottom: 48,
    });

    const event = new MouseEvent('mousedown', {
      bubbles: true,
      cancelable: true,
      button: 0,
      clientX: 80,
      clientY: 640,
    });
    query<HTMLElement>('.cm-scroller').dispatchEvent(event);

    expect(view.state.selection.main.anchor).toBe(view.state.doc.length);
    expect(document.activeElement).toBe(contentElement());
    expect(event.defaultPrevented).toBe(true);
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

  it('supplies the localized wiki-link registry to CodeMirror state', () => {
    const view = editorView();
    view.dispatch({
      changes: { from: 0, to: view.state.doc.length, insert: '[[matrix:' },
      selection: { anchor: '[[matrix:'.length },
    });

    const result = wikiLinkCompletionSource(
      new CompletionContext(view.state, view.state.selection.main.head, false),
    );

    expect(result?.options).toEqual([
      expect.objectContaining({
        label: 'known-question',
        wikiLinkTitle: 'Известный вопрос',
        wikiLinkStatus: 'Черновик',
      }),
    ]);
    expect(wikiLinkTargetsService.getTargets).toHaveBeenCalledWith('ru');
  });

  it('updates localized completion titles on language change without rebuilding the editor', () => {
    const view = editorView();
    view.dispatch({
      changes: { from: 0, to: view.state.doc.length, insert: '[[matrix:' },
      selection: { anchor: '[[matrix:'.length },
    });

    fixture.componentRef.setInput('language', 'en');
    fixture.detectChanges();

    const result = wikiLinkCompletionSource(
      new CompletionContext(view.state, view.state.selection.main.head, false),
    );
    expect(editorView()).toBe(view);
    expect(result?.options).toEqual([
      expect.objectContaining({
        label: 'known-question',
        wikiLinkTitle: 'Known question',
        wikiLinkStatus: 'Черновик',
      }),
    ]);
    expect(wikiLinkTargetsService.getTargets).toHaveBeenCalledWith('en');
  });

  it('keeps manual editing available when the target registry cannot be loaded', () => {
    wikiLinkTargetsService.getTargets.mockImplementation((language: string) =>
      language === 'en'
        ? throwError(() => new Error('registry unavailable'))
        : of(RU_WIKI_LINK_REGISTRY),
    );
    fixture.componentRef.setInput('language', 'en');
    fixture.detectChanges();
    const view = editorView();

    view.dispatch({
      changes: { from: 0, to: view.state.doc.length, insert: '[[matrix:manual-link]]' },
      selection: { anchor: '[[matrix:manual-link'.length },
    });
    fixture.detectChanges();

    expect(view.state.doc.toString()).toBe('[[matrix:manual-link]]');
    expect(query<HTMLElement>('.markdown-editor-status').textContent).toContain(
      'Не удалось загрузить варианты wiki-ссылок.',
    );
  });

  it('supports strict domain filtering and keyboard-first chained completion', async () => {
    const view = editorView();
    replaceEditorDocument(view, '[[m]]', 3);

    await waitForAutocomplete();

    expect(completionLabels()).toEqual(['matrix']);
    expect(
      query<HTMLElement>('.cm-tooltip-autocomplete [role="listbox"]').getAttribute('aria-label'),
    ).toBe('Варианты');
    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'Enter',
        key: 'Enter',
      }),
    );
    await waitForAutocomplete();

    expect(view.state.doc.toString()).toBe('[[matrix:]]');
    expect(completionLabels()).toEqual(['known-question']);
    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'Enter',
        key: 'Enter',
      }),
    );

    expect(view.state.doc.toString()).toBe('[[matrix:known-question]]');
    expect(view.state.selection.main.head).toBe(view.state.doc.toString().indexOf(']]'));
  });

  it('shows the human title and status above the slug without a generic text icon', async () => {
    replaceEditorDocument(editorView(), '[[matrix:]]', '[[matrix:'.length);

    await waitForAutocomplete();

    const option = query<HTMLElement>('.cm-wiki-link-completion-option');
    const metadata = query<HTMLElement>(
      '.cm-wiki-link-completion-option .cm-wiki-link-completion-metadata',
    );
    const slug = query<HTMLElement>('.cm-wiki-link-completion-option .cm-completionLabel');
    expect(option.querySelector('.cm-completionIcon')).toBeNull();
    expect(metadata.textContent).toContain('Известный вопрос');
    expect(metadata.textContent).toContain('Черновик');
    expect(slug.textContent).toBe('known-question');
    expect(metadata.compareDocumentPosition(slug) & Node.DOCUMENT_POSITION_FOLLOWING).not.toBe(0);
  });

  it('uses ArrowDown and Escape without moving or changing the typed fragment', async () => {
    const view = editorView();
    replaceEditorDocument(view, '[[]]', 2);
    await waitForAutocomplete();
    const cursor = view.state.selection.main.head;

    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'ArrowDown',
        key: 'ArrowDown',
      }),
    );
    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'Escape',
        key: 'Escape',
      }),
    );

    expect(view.state.doc.toString()).toBe('[[]]');
    expect(view.state.selection.main.head).toBe(cursor);
    expect(fixture.nativeElement.querySelector('.cm-tooltip-autocomplete')).toBeNull();
  });

  it('applies a mouse-selected target with the same minimal transaction', async () => {
    const view = editorView();
    replaceEditorDocument(view, '[[matrix:kn]]', '[[matrix:kn'.length);
    await waitForAutocomplete();
    const option = query<HTMLElement>('.cm-tooltip-autocomplete li');

    option.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));

    expect(view.state.doc.toString()).toBe('[[matrix:known-question]]');
    expect(view.state.selection.main.head).toBe(view.state.doc.toString().indexOf(']]'));
  });

  it('does not accept a completion during IME composition', async () => {
    const view = editorView();
    replaceEditorDocument(view, '[[matrix:kn]]', '[[matrix:kn'.length);
    await waitForAutocomplete();

    contentElement().dispatchEvent(
      new CompositionEvent('compositionstart', {
        bubbles: true,
        data: 'в',
      }),
    );
    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'Enter',
        key: 'Enter',
        isComposing: true,
      }),
    );

    expect(view.state.doc.toString()).not.toBe('[[matrix:known-question]]');
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

  it('exposes an accessible expand and collapse control in source and preview modes', () => {
    const shell = query<HTMLElement>('[data-testid="markdown-editor-shell"]');
    const toggle = query<HTMLButtonElement>('[data-testid="markdown-editor-fullscreen-toggle"]');
    const focusTrap = fixture.debugElement
      .query(By.css('[data-testid="markdown-editor-shell"]'))
      .injector.get(CdkTrapFocus);
    const initialIconPath = toggle.querySelector('path')?.getAttribute('d');

    expect(toggle.getAttribute('aria-label')).toBe('Развернуть редактор на весь экран');
    expect(toggle.getAttribute('title')).toBe('Развернуть редактор на весь экран');
    expect(toggle.getAttribute('aria-pressed')).toBe('false');
    expect(shell.getAttribute('role')).toBeNull();
    expect(shell.getAttribute('aria-modal')).toBeNull();
    expect(focusTrap.enabled).toBe(false);

    toggle.click();
    fixture.detectChanges();

    expect(shell.classList).toContain('markdown-editor-fullscreen');
    expect(shell.getAttribute('role')).toBe('dialog');
    expect(shell.getAttribute('aria-modal')).toBe('true');
    expect(shell.getAttribute('aria-label')).toBe('Содержимое статьи RU');
    expect(toggle.getAttribute('aria-label')).toBe('Выйти из полноэкранного режима');
    expect(toggle.getAttribute('title')).toBe('Выйти из полноэкранного режима');
    expect(toggle.getAttribute('aria-pressed')).toBe('true');
    expect(toggle.querySelector('path')?.getAttribute('d')).not.toBe(initialIconPath);
    expect(acquirePageScrollLock).toHaveBeenCalledTimes(1);
    expect(focusTrap.enabled).toBe(true);

    query<HTMLButtonElement>('[data-testid="markdown-editor-preview-tab"]').click();
    fixture.detectChanges();

    expect(query<HTMLButtonElement>('[data-testid="markdown-editor-fullscreen-toggle"]')).toBe(
      toggle,
    );
    expect(fixture.componentInstance.mode()).toBe('preview');
  });

  it('exits fullscreen with Escape without closing an owning modal and restores focus', () => {
    const frameCallbacks: FrameRequestCallback[] = [];
    const requestAnimationFrame = jest
      .spyOn(window, 'requestAnimationFrame')
      .mockImplementation((callback) => {
        frameCallbacks.push(callback);
        return frameCallbacks.length;
      });
    const opener = document.createElement('button');
    document.body.append(opener);
    opener.focus();
    const toggle = query<HTMLButtonElement>('[data-testid="markdown-editor-fullscreen-toggle"]');
    const owningModalKeydown = jest.fn();
    const owningModalKeyup = jest.fn();
    fixture.nativeElement.addEventListener('keydown', owningModalKeydown);
    document.addEventListener('keyup', owningModalKeyup);

    toggle.click();
    fixture.detectChanges();
    frameCallbacks.shift()?.(0);
    expect(document.activeElement).toBe(toggle);

    const escape = new KeyboardEvent('keydown', {
      bubbles: true,
      cancelable: true,
      code: 'Escape',
      key: 'Escape',
    });
    toggle.dispatchEvent(escape);
    fixture.detectChanges();
    while (frameCallbacks.length > 0) {
      frameCallbacks.shift()?.(16);
    }
    const escapeKeyup = new KeyboardEvent('keyup', {
      bubbles: true,
      cancelable: true,
      code: 'Escape',
      key: 'Escape',
    });
    opener.dispatchEvent(escapeKeyup);

    expect(escape.defaultPrevented).toBe(true);
    expect(escapeKeyup.defaultPrevented).toBe(true);
    expect(owningModalKeydown).not.toHaveBeenCalled();
    expect(owningModalKeyup).not.toHaveBeenCalled();
    expect(document.activeElement).toBe(opener);
    expect(query<HTMLElement>('[data-testid="markdown-editor-shell"]').classList).not.toContain(
      'markdown-editor-fullscreen',
    );
    expect(releasePageScrollLock).toHaveBeenCalledTimes(1);

    requestAnimationFrame.mockRestore();
    document.removeEventListener('keyup', owningModalKeyup);
    opener.remove();
  });

  it('lets an open editor surface consume Escape before fullscreen exits', () => {
    const toggle = query<HTMLButtonElement>('[data-testid="markdown-editor-fullscreen-toggle"]');
    const shortcuts = query<HTMLDetailsElement>('[data-testid="markdown-editor-shortcuts"]');
    const summary = query<HTMLElement>('[data-testid="markdown-editor-shortcuts-summary"]');
    toggle.click();
    fixture.detectChanges();
    summary.click();
    expect(shortcuts.open).toBe(true);

    summary.dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'Escape',
        key: 'Escape',
      }),
    );
    fixture.detectChanges();

    expect(shortcuts.open).toBe(false);
    expect(query<HTMLElement>('[data-testid="markdown-editor-shell"]').classList).toContain(
      'markdown-editor-fullscreen',
    );
    expect(releasePageScrollLock).not.toHaveBeenCalled();
  });

  it('does not exit fullscreen while an IME composition owns Escape', () => {
    const toggle = query<HTMLButtonElement>('[data-testid="markdown-editor-fullscreen-toggle"]');
    toggle.click();
    fixture.detectChanges();

    contentElement().dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'Escape',
        key: 'Escape',
        isComposing: true,
      }),
    );
    fixture.detectChanges();

    expect(query<HTMLElement>('[data-testid="markdown-editor-shell"]').classList).toContain(
      'markdown-editor-fullscreen',
    );
    expect(releasePageScrollLock).not.toHaveBeenCalled();
  });

  it('restores the nearest external scroll container after fullscreen', () => {
    const scrollContainer = document.createElement('div');
    scrollContainer.style.overflowY = 'auto';
    Object.defineProperty(scrollContainer, 'clientHeight', {
      configurable: true,
      value: 600,
    });
    Object.defineProperty(scrollContainer, 'scrollHeight', {
      configurable: true,
      value: 12_000,
    });
    document.body.append(scrollContainer);
    scrollContainer.append(fixture.nativeElement);
    scrollContainer.scrollTop = 4_200;
    const frameCallbacks: FrameRequestCallback[] = [];
    const requestAnimationFrame = jest
      .spyOn(window, 'requestAnimationFrame')
      .mockImplementation((callback) => {
        frameCallbacks.push(callback);
        return frameCallbacks.length;
      });
    const toggle = query<HTMLButtonElement>('[data-testid="markdown-editor-fullscreen-toggle"]');

    toggle.click();
    fixture.detectChanges();
    frameCallbacks.shift()?.(0);
    scrollContainer.scrollTop = 135;
    toggle.dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'Escape',
        key: 'Escape',
      }),
    );
    fixture.detectChanges();
    while (frameCallbacks.length > 0) {
      frameCallbacks.shift()?.(16);
    }

    expect(scrollContainer.scrollTop).toBe(4_200);

    requestAnimationFrame.mockRestore();
    scrollContainer.remove();
  });

  it('preserves unsaved document, history, and multi-selection across fullscreen', () => {
    const emitted: string[] = [];
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    const view = editorView();
    view.dispatch({
      changes: { from: 0, insert: 'Draft ' },
      selection: EditorSelection.create([EditorSelection.range(1, 4), EditorSelection.cursor(10)]),
      userEvent: 'input.type',
    });
    const unsavedDocument = view.state.doc.toString();
    const selections = view.state.selection.ranges.map(({ anchor, head }) => ({ anchor, head }));
    const toggle = query<HTMLButtonElement>('[data-testid="markdown-editor-fullscreen-toggle"]');

    toggle.click();
    fixture.detectChanges();
    toggle.dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        code: 'Escape',
        key: 'Escape',
      }),
    );
    fixture.detectChanges();

    expect(editorView()).toBe(view);
    expect(view.state.doc.toString()).toBe(unsavedDocument);
    expect(view.state.selection.ranges.map(({ anchor, head }) => ({ anchor, head }))).toEqual(
      selections,
    );
    expect(emitted).toEqual([unsavedDocument]);
    expect(undo(view)).toBe(true);
    expect(view.state.doc.toString()).toBe('Initial **markdown**');
  });

  it('releases its fullscreen page lock when destroyed', () => {
    query<HTMLButtonElement>('[data-testid="markdown-editor-fullscreen-toggle"]').click();
    fixture.detectChanges();

    fixture.destroy();

    expect(releasePageScrollLock).toHaveBeenCalledTimes(1);
  });

  it('renders every source command as an accessible icon action and hides it in preview', () => {
    const toolbar = query<HTMLElement>('[data-testid="markdown-editor-toolbar"]');
    const expectedCommandIds = MARKDOWN_EDITOR_SHORTCUT_GROUPS.flatMap((group) =>
      group.commandIds.filter((commandId) => commandId !== 'togglePreview'),
    );
    const commandButtons = Array.from(
      toolbar.querySelectorAll<HTMLButtonElement>('[data-markdown-command]'),
    );

    expect(toolbar.getAttribute('aria-label')).toBe('Действия Markdown-редактора');
    expect(commandButtons.map((button) => button.dataset['markdownCommand'])).toEqual(
      expectedCommandIds,
    );
    expect(
      toolbar
        .querySelector<HTMLButtonElement>('[data-markdown-command="bold"]')
        ?.getAttribute('aria-label'),
    ).toBe('Жирный (Ctrl + B)');
    expect(
      toolbar
        .querySelector<HTMLButtonElement>('[data-markdown-command="bold"]')
        ?.getAttribute('title'),
    ).toBe('Жирный (Ctrl + B)');
    expect(
      commandButtons.every((button) => {
        const icon = button.querySelector<SVGElement>('.markdown-editor-toolbar-icon');
        return (
          button.textContent?.trim() === '' &&
          icon !== null &&
          (icon.querySelector('path')?.getAttribute('d')?.length ?? 0) > 0
        );
      }),
    ).toBe(true);

    query<HTMLButtonElement>('[data-testid="markdown-editor-preview-tab"]').click();
    fixture.detectChanges();

    expect(
      fixture.nativeElement.querySelector('[data-testid="markdown-editor-toolbar"]'),
    ).toBeNull();
  });

  it('uses roving focus across toolbar commands', () => {
    const buttons = Array.from(
      query<HTMLElement>(
        '[data-testid="markdown-editor-toolbar"]',
      ).querySelectorAll<HTMLButtonElement>('[data-markdown-command]'),
    );
    buttons[0]?.focus();

    buttons[0]?.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
    expect(document.activeElement).toBe(buttons[1]);

    buttons[1]?.dispatchEvent(new KeyboardEvent('keydown', { key: 'End', bubbles: true }));
    expect(document.activeElement).toBe(buttons.at(-1));

    buttons.at(-1)?.dispatchEvent(new KeyboardEvent('keydown', { key: 'Home', bubbles: true }));
    expect(document.activeElement).toBe(buttons[0]);
  });

  it('applies toolbar commands through the current editor selection and restores focus', () => {
    const view = editorView();
    view.dispatch({ selection: { anchor: 0, head: 7 } });
    query<HTMLButtonElement>('[data-markdown-command="bold"]').click();
    fixture.detectChanges();

    expect(view.state.doc.toString()).toBe('**Initial** **markdown**');
    expect(document.activeElement).toBe(contentElement());
  });

  it('applies snippet toolbar commands through the shared command path', () => {
    const view = editorView();
    view.dispatch({ selection: { anchor: view.state.doc.length } });

    query<HTMLButtonElement>('[data-markdown-command="table"]').click();
    fixture.detectChanges();

    expect(view.state.doc.toString()).toContain('|  |  |');
    expect(view.state.doc.toString()).toContain('| --- | --- |');
    expect(document.activeElement).toBe(contentElement());
  });

  it('opens search and image selection from toolbar actions', () => {
    const imageInput = query<HTMLInputElement>('input[type="file"]');
    const imagePicker = jest.spyOn(imageInput, 'click').mockImplementation(() => undefined);

    query<HTMLButtonElement>('[data-markdown-command="search"]').click();
    fixture.detectChanges();
    const searchInput = query<HTMLInputElement>('.cm-search input[name="search"]');
    expect(searchInput.placeholder).toBe('Найти');
    expect(document.activeElement).toBe(searchInput);

    query<HTMLButtonElement>('[data-markdown-command="image"]').click();
    expect(imagePicker).toHaveBeenCalledTimes(1);
  });

  it('keeps the image insertion position captured by the toolbar command', () => {
    const emitted: string[] = [];
    const view = editorView();
    const imageInput = query<HTMLInputElement>('input[type="file"]');
    const file = new File(['picked'], 'picked.png', { type: 'image/png' });
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    uploadService.uploadEditorImage.mockReturnValue(of('https://cdn.example.com/picked.png'));
    jest.spyOn(imageInput, 'click').mockImplementation(() => undefined);
    view.dispatch({ selection: { anchor: 8 } });

    query<HTMLButtonElement>('[data-markdown-command="image"]').click();
    view.dispatch({ selection: { anchor: 0 } });
    Object.defineProperty(imageInput, 'files', { configurable: true, value: [file] });
    imageInput.dispatchEvent(new Event('change', { bubbles: true }));
    fixture.detectChanges();

    expect(emitted.at(-1)).toBe(
      'Initial ![picked.png](https://cdn.example.com/picked.png)**markdown**',
    );
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

  it('opens only preview wiki-links in a new tab with opener isolation', () => {
    const open = jest.spyOn(window, 'open').mockImplementation(() => null);
    fixture.componentRef.setInput(
      'value',
      '[[articles:example|Wiki article]] and [ordinary article](/ru/articles/ordinary)',
    );
    fixture.detectChanges();
    query<HTMLButtonElement>('[data-testid="markdown-editor-preview-tab"]').click();
    fixture.detectChanges();
    const links = Array.from(
      query<HTMLElement>('[data-testid="markdown-editor-preview-content"]').querySelectorAll('a'),
    );
    const wikiLink = links.find((link) => link.textContent === 'Wiki article');
    const ordinaryLink = links.find((link) => link.textContent === 'ordinary article');
    if (wikiLink === undefined || ordinaryLink === undefined) {
      throw new Error('Missing preview links');
    }

    const wikiClick = new MouseEvent('click', { bubbles: true, cancelable: true });
    wikiLink.dispatchEvent(wikiClick);
    const ordinaryClick = new MouseEvent('click', { bubbles: true, cancelable: true });
    ordinaryLink.dispatchEvent(ordinaryClick);

    expect(wikiClick.defaultPrevented).toBe(true);
    expect(ordinaryClick.defaultPrevented).toBe(false);
    expect(open).toHaveBeenCalledWith('/ru/articles/example', '_blank', 'noopener,noreferrer');
    open.mockRestore();
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

  it('restores editor focus without restoring editor-owned scroll', () => {
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
    scroller.scrollTop = 11;

    expect(scroller.scrollTop).toBe(11);
    expect(document.activeElement).toBe(contentElement());
  });

  it('preserves the nearest external scroll container when switching modes', () => {
    const scrollContainer = document.createElement('div');
    scrollContainer.style.overflowY = 'auto';
    Object.defineProperty(scrollContainer, 'clientHeight', {
      configurable: true,
      value: 600,
    });
    Object.defineProperty(scrollContainer, 'scrollHeight', {
      configurable: true,
      value: 12_000,
    });
    document.body.append(scrollContainer);
    scrollContainer.append(fixture.nativeElement);
    scrollContainer.scrollTop = 4_200;
    const frameCallbacks: FrameRequestCallback[] = [];
    const requestAnimationFrame = jest
      .spyOn(window, 'requestAnimationFrame')
      .mockImplementation((callback) => {
        frameCallbacks.push(callback);
        return frameCallbacks.length;
      });

    fixture.componentInstance.selectMode('preview');
    fixture.detectChanges();
    scrollContainer.scrollTop = 3_943;
    frameCallbacks.shift()?.(0);
    scrollContainer.scrollTop = 3_943;
    frameCallbacks.shift()?.(16);

    expect(scrollContainer.scrollTop).toBe(4_200);

    requestAnimationFrame.mockRestore();
    scrollContainer.remove();
  });

  it('reports sticky header and footer heights as CodeMirror scroll margins', () => {
    const header = query<HTMLElement>('[data-testid="markdown-editor-header"]');
    const footer = query<HTMLElement>('[data-testid="markdown-editor-footer"]');
    Object.defineProperty(header, 'offsetHeight', { configurable: true, value: 72 });
    Object.defineProperty(footer, 'offsetHeight', { configurable: true, value: 48 });
    const view = editorView();
    const margins = view.state
      .facet(EditorView.scrollMargins)
      .map((provideMargins) => provideMargins(view));

    expect(margins).toContainEqual({ top: 72, bottom: 48 });
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

  it('closes the shortcut panel with Escape and restores summary focus', () => {
    const shortcuts = query<HTMLDetailsElement>('[data-testid="markdown-editor-shortcuts"]');
    const summary = query<HTMLElement>('[data-testid="markdown-editor-shortcuts-summary"]');
    const outerKeyup = jest.fn();
    fixture.nativeElement.addEventListener('keyup', outerKeyup);
    summary.click();
    expect(shortcuts.open).toBe(true);

    summary.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }),
    );
    summary.dispatchEvent(
      new KeyboardEvent('keyup', { key: 'Escape', bubbles: true, cancelable: true }),
    );

    expect(shortcuts.open).toBe(false);
    expect(document.activeElement).toBe(summary);
    expect(outerKeyup).not.toHaveBeenCalled();
  });

  function editorElement(): HTMLElement {
    return query<HTMLElement>('.cm-editor');
  }

  function contentElement(): HTMLElement {
    return query<HTMLElement>('.cm-content');
  }

  function editorView(): EditorView {
    const view = EditorView.findFromDOM(contentElement());
    if (view === null) {
      throw new Error('Missing EditorView');
    }
    return view;
  }

  function completionLabels(): string[] {
    return Array.from(
      fixture.nativeElement.querySelectorAll<HTMLElement>(
        '.cm-tooltip-autocomplete .cm-completionLabel',
      ),
      (label) => label.textContent ?? '',
    );
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
    const acquirePageScrollLock = jest.fn();
    await TestBed.configureTestingModule({
      imports: [MarkdownEditorComponent],
      providers: [
        { provide: PLATFORM_ID, useValue: 'server' },
        {
          provide: ModalPageScrollLockService,
          useValue: { acquire: acquirePageScrollLock },
        },
        {
          provide: EditorImageUploadService,
          useValue: { uploadEditorImage: jest.fn() },
        },
        {
          provide: WikiLinkTargetsService,
          useValue: { getTargets: jest.fn() },
        },
        provideI18nTesting(EDITOR_MESSAGES),
      ],
    }).compileComponents();
    const fixture = TestBed.createComponent(MarkdownEditorComponent);
    fixture.componentRef.setInput('value', 'Server Markdown');
    fixture.componentRef.setInput('language', 'en');
    fixture.componentRef.setInput('accessibleLabel', 'Article content');
    fixture.componentRef.setInput('imageUploadsEnabled', true);

    expect(() => fixture.detectChanges()).not.toThrow();
    expect(fixture.nativeElement.querySelector('.cm-editor')).toBeNull();
    expect(TestBed.inject(WikiLinkTargetsService).getTargets).not.toHaveBeenCalled();
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="markdown-editor-fullscreen-toggle"]')
      ?.click();
    fixture.detectChanges();
    expect(acquirePageScrollLock).not.toHaveBeenCalled();
    expect(
      fixture.nativeElement.querySelector('[data-testid="markdown-editor-shell"]')?.classList,
    ).not.toContain('markdown-editor-fullscreen');
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
      getData: () => '',
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

function replaceEditorDocument(view: EditorView, document: string, cursor: number): void {
  view.dispatch({
    changes: { from: 0, to: view.state.doc.length, insert: document },
    selection: { anchor: cursor },
    userEvent: 'input.type',
  });
}

async function waitForAutocomplete(): Promise<void> {
  await new Promise((resolve) => window.setTimeout(resolve, 500));
}
