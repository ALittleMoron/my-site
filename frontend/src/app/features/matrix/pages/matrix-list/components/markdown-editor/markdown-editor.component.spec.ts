import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { FileUploadService } from '../../../../services/file-upload.service';
import { MarkdownEditorComponent } from './markdown-editor.component';

interface MockEditorOptions {
  initialValue?: string;
  events?: {
    change?: () => void;
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

  beforeEach(async () => {
    MockEditor.instances = [];
    MockEditor.setLanguage.mockClear();
    uploadService = {
      uploadEditorImage: jest.fn().mockReturnValue(of('https://cdn.example.com/image.png')),
    };

    await TestBed.configureTestingModule({
      imports: [MarkdownEditorComponent],
      providers: [{ provide: FileUploadService, useValue: uploadService }],
    }).compileComponents();

    fixture = TestBed.createComponent(MarkdownEditorComponent);
    fixture.componentRef.setInput('value', 'Initial **markdown**');
  });

  it('lazy-loads ToastUI editor with the current value', async () => {
    fixture.detectChanges();
    await fixture.whenStable();

    expect(MockEditor.setLanguage).toHaveBeenCalledWith('ru-RU', { Markdown: 'Markdown' });
    expect(MockEditor.instances[0].options.initialValue).toBe('Initial **markdown**');
  });

  it('emits markdown changes from the editor', async () => {
    const emitted: string[] = [];
    fixture.componentInstance.valueChange.subscribe((value) => emitted.push(value));
    fixture.detectChanges();
    await fixture.whenStable();

    MockEditor.instances[0].setMarkdown('Updated');
    MockEditor.instances[0].options.events?.change?.();

    expect(emitted).toEqual(['Updated']);
  });

  it('uploads image blobs through FileUploadService', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    const callback = jest.fn();
    const blob = new Blob(['image'], { type: 'image/png' });

    MockEditor.instances[0].options.hooks?.addImageBlobHook?.(blob, callback);

    expect(uploadService.uploadEditorImage).toHaveBeenCalledWith(blob);
    expect(callback).toHaveBeenCalledWith('https://cdn.example.com/image.png', 'image');
  });

  it('destroys the editor instance', async () => {
    fixture.detectChanges();
    await fixture.whenStable();

    fixture.destroy();

    expect(MockEditor.instances[0].destroy).toHaveBeenCalled();
  });
});
