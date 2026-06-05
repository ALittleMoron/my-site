import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  OnDestroy,
  ViewChild,
  effect,
  inject,
  input,
  output,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import type Editor from '@toast-ui/editor';
import { I18nService } from '../i18n/i18n.service';
import { ThemeService } from '../layout/theme.service';
import { EditorImageUploadService } from './editor-image-upload.service';

@Component({
  selector: 'app-markdown-editor',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: '<div class="markdown-editor" #editorHost></div>',
})
export class MarkdownEditorComponent implements AfterViewInit, OnDestroy {
  private readonly imageUpload = inject(EditorImageUploadService);
  private readonly i18n = inject(I18nService);
  private readonly themeService = inject(ThemeService);
  private readonly destroyRef = inject(DestroyRef);
  private editor: Editor | null = null;
  private syncingInput = false;

  @ViewChild('editorHost', { static: true }) private readonly editorHost!: ElementRef<HTMLElement>;

  readonly value = input<string>('');
  readonly valueChange = output<string>();

  constructor() {
    effect(() => {
      const value = this.value();
      if (!this.editor || this.editor.getMarkdown() === value) return;
      this.syncingInput = true;
      this.editor.setMarkdown(value, false);
      this.syncingInput = false;
    });
  }

  async ngAfterViewInit(): Promise<void> {
    const { default: Editor } = await import('@toast-ui/editor');
    const language = await this.resolveEditorLanguage(Editor);
    this.editor = new Editor({
      el: this.editorHost.nativeElement,
      height: '360px',
      initialEditType: 'markdown',
      hideModeSwitch: true,
      language,
      previewStyle: 'vertical',
      usageStatistics: false,
      initialValue: this.value(),
      ...(this.themeService.theme() === 'dark' ? { theme: 'dark' as const } : {}),
      toolbarItems: [
        ['heading', 'bold', 'italic', 'strike'],
        ['hr', 'quote', 'ul', 'ol', 'task'],
        ['table', 'link', 'image', 'code', 'codeblock'],
      ],
      events: {
        change: () => {
          if (!this.syncingInput) {
            this.valueChange.emit(this.editor?.getMarkdown() ?? '');
          }
        },
      },
      hooks: {
        addImageBlobHook: (blob, callback) => {
          this.imageUpload
            .uploadEditorImage(blob)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
              next: (accessUrl) => callback(accessUrl, 'image'),
            });
        },
      },
    });
  }

  ngOnDestroy(): void {
    this.editor?.destroy();
  }

  private async resolveEditorLanguage(editorConstructor: typeof Editor): Promise<string> {
    if (this.i18n.language() !== 'ru') {
      return 'en-US';
    }
    const { default: ruRu } = await import('@toast-ui/editor/dist/i18n/ru-ru');
    editorConstructor.setLanguage('ru-RU', ruRu);
    return 'ru-RU';
  }
}
