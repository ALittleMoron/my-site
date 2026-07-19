import { signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { ThemeService } from '../layout/theme.service';
import { provideI18nTesting } from '../../testing/i18n-testing';
import { EditorImageUploadService } from './editor-image-upload.service';
import { MarkdownEditorComponent } from './markdown-editor.component';

interface MockEditorOptions {
  autofocus?: boolean;
  initialValue?: string;
  plugins?: unknown[];
  theme?: string;
  events?: {
    change?: () => void;
    keyup?: (editorType: 'markdown' | 'wysiwyg', event: KeyboardEvent) => void;
  };
  hooks?: {
    addImageBlobHook?: (blob: Blob, callback: (url: string, altText?: string) => void) => void;
  };
}

class MockEditor {
  static setLanguage = jest.fn();
  static instances: MockEditor[] = [];

  readonly options: MockEditorOptions;
  private markdown: string;
  private selection: [[number, number], [number, number]] = [
    [1, 1],
    [1, 1],
  ];

  constructor(options: MockEditorOptions) {
    this.options = options;
    this.markdown = options.initialValue ?? '';
    MockEditor.instances.push(this);
  }

  getMarkdown(): string {
    return this.markdown;
  }

  setMarkdown(markdown: string): void {
    this.markdown = markdown;
  }

  getSelection(): [[number, number], [number, number]] {
    return this.selection;
  }

  insertText = jest.fn();

  setSelection = jest.fn((start: [number, number], end: [number, number] = start) => {
    this.selection = [start, end];
  });

  destroy = jest.fn();
}

jest.mock('@toast-ui/editor', () => ({
  __esModule: true,
  default: MockEditor,
}));

jest.mock('@toast-ui/editor/dist/i18n/ru-ru', () => ({
  __esModule: true,
  default: { Markdown: 'Markdown' },
}));

describe('MarkdownEditorComponent', () => {
  let fixture: ComponentFixture<MarkdownEditorComponent>;
  let uploadService: { uploadEditorImage: jest.Mock };
  let themeService: { theme: ReturnType<typeof signal<'light' | 'dark'>> };

  beforeEach(async () => {
    removeEditorStylesheetLinks();
    MockEditor.instances = [];
    MockEditor.setLanguage.mockClear();
    uploadService = {
      uploadEditorImage: jest.fn().mockReturnValue(of('https://cdn.example.com/image.png')),
    };
    themeService = {
      theme: signal<'light' | 'dark'>('dark'),
    };

    await TestBed.configureTestingModule({
      imports: [MarkdownEditorComponent],
      providers: [
        { provide: EditorImageUploadService, useValue: uploadService },
        { provide: ThemeService, useValue: themeService },
        provideI18nTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MarkdownEditorComponent);
    fixture.componentRef.setInput('value', 'Initial **markdown**');
  });

  afterEach(() => {
    removeEditorStylesheetLinks();
  });

  it('lazy-loads ToastUI editor with the current value', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);

    expect(MockEditor.setLanguage).toHaveBeenCalledWith('ru-RU', { Markdown: 'Markdown' });
    expect(MockEditor.instances[0].options.initialValue).toBe('Initial **markdown**');
  });

  it('does not take focus when the editor is initialized', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);

    expect(MockEditor.instances[0].options.autofocus).toBe(false);
  });

  it('loads Toast UI stylesheets before creating the editor', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);

    const styleLinks = Array.from(document.head.querySelectorAll('link[rel="stylesheet"]')).map(
      (link) => link.getAttribute('href'),
    );

    expect(styleLinks).toContain('/toastui-editor.css');
    expect(styleLinks).toContain('/toastui-editor-dark.css');
    expect(styleLinks).toContain('/toastui-editor-code-syntax-highlight.css');
  });

  it('configures code syntax highlighting for the preview', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);

    expect(MockEditor.instances[0].options.plugins).toHaveLength(1);
  });

  it('uses Toast UI dark theme when the app theme is dark', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);

    expect(MockEditor.instances[0].options.theme).toBe('dark');
  });

  it('emits markdown changes from the editor', async () => {
    const emitted: string[] = [];
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    fixture.detectChanges();
    await waitForEditor(fixture);

    MockEditor.instances[0].setMarkdown('Updated');
    MockEditor.instances[0].options.events?.change?.();

    expect(emitted).toEqual(['Updated']);
  });

  it('inserts a closing code fence after the third backtick and keeps the cursor at the opener', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);
    const editor = MockEditor.instances[0];
    editor.setMarkdown('```');
    editor.setSelection([1, 4]);
    editor.setSelection.mockClear();

    editor.options.events?.keyup?.('markdown', new KeyboardEvent('keyup', { key: '`' }));

    expect(editor.insertText).toHaveBeenCalledWith('\n```');
    expect(editor.setSelection).toHaveBeenCalledWith([1, 4]);
  });

  it('does not duplicate an existing closing code fence', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);
    const editor = MockEditor.instances[0];
    editor.setMarkdown('```\n```');
    editor.setSelection([1, 4]);
    editor.insertText.mockClear();

    editor.options.events?.keyup?.('markdown', new KeyboardEvent('keyup', { key: '`' }));

    expect(editor.insertText).not.toHaveBeenCalled();
  });

  it('does not auto-close a code fence when the third backtick closes an open block', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);
    const editor = MockEditor.instances[0];
    editor.setMarkdown('```ts\nconst answer = 42;\n```');
    editor.setSelection([3, 4]);
    editor.insertText.mockClear();

    editor.options.events?.keyup?.('markdown', new KeyboardEvent('keyup', { key: '`' }));

    expect(editor.insertText).not.toHaveBeenCalled();
  });

  it('does not auto-close inline backticks or react to other keys', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);
    const editor = MockEditor.instances[0];
    editor.setMarkdown('Text ```');
    editor.setSelection([1, 9]);

    editor.options.events?.keyup?.('markdown', new KeyboardEvent('keyup', { key: '`' }));
    editor.setMarkdown('```');
    editor.setSelection([1, 4]);
    editor.options.events?.keyup?.('markdown', new KeyboardEvent('keyup', { key: 'Enter' }));

    expect(editor.insertText).not.toHaveBeenCalled();
  });

  it('does not auto-close a code fence for a selection or in WYSIWYG mode', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);
    const editor = MockEditor.instances[0];
    editor.setMarkdown('```');
    editor.setSelection([1, 1], [1, 4]);

    editor.options.events?.keyup?.('markdown', new KeyboardEvent('keyup', { key: '`' }));
    editor.setSelection([1, 4]);
    editor.options.events?.keyup?.('wysiwyg', new KeyboardEvent('keyup', { key: '`' }));

    expect(editor.insertText).not.toHaveBeenCalled();
  });

  it('uploads image blobs through EditorImageUploadService', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);
    const callback = jest.fn();
    const blob = new Blob(['image'], { type: 'image/png' });

    MockEditor.instances[0].options.hooks?.addImageBlobHook?.(blob, callback);

    expect(uploadService.uploadEditorImage).toHaveBeenCalledWith(blob);
    expect(callback).toHaveBeenCalledWith('https://cdn.example.com/image.png', 'image');
  });

  it('destroys the editor instance', async () => {
    fixture.detectChanges();
    await waitForEditor(fixture);

    fixture.destroy();

    expect(MockEditor.instances[0].destroy).toHaveBeenCalled();
  });
});

async function waitForEditor(fixture: ComponentFixture<MarkdownEditorComponent>): Promise<void> {
  for (let attempt = 0; attempt < 5 && MockEditor.instances.length === 0; attempt += 1) {
    await fixture.whenStable();
    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });
  }
}

function removeEditorStylesheetLinks(): void {
  document
    .querySelectorAll(
      'link[href="/toastui-editor.css"], link[href="/toastui-editor-dark.css"], link[href="/toastui-editor-code-syntax-highlight.css"]',
    )
    .forEach((link) => link.remove());
}
