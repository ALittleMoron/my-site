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
import { FileUploadService } from '../../../../services/file-upload.service';

@Component({
  selector: 'app-markdown-editor',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: '<div class="markdown-editor" #editorHost></div>',
})
export class MarkdownEditorComponent implements AfterViewInit, OnDestroy {
  private readonly fileUploadService = inject(FileUploadService);
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
    const [{ default: Editor }, { default: ruRu }] = await Promise.all([
      import('@toast-ui/editor'),
      import('@toast-ui/editor/dist/i18n/ru-ru'),
    ]);
    Editor.setLanguage('ru-RU', ruRu);
    this.editor = new Editor({
      el: this.editorHost.nativeElement,
      height: '360px',
      initialEditType: 'markdown',
      hideModeSwitch: true,
      language: 'ru-RU',
      previewStyle: 'vertical',
      usageStatistics: false,
      initialValue: this.value(),
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
          this.fileUploadService
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
}
