import { ChangeDetectionStrategy, Component, computed, input, output } from '@angular/core';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import { ApiError } from '../../../../../../core/models/api-error.model';
import { ErrorMessageComponent } from '../../../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../../../shared/ui/loading-spinner/loading-spinner.component';
import { NoteDetail } from '../../../../models/notes.model';

@Component({
  selector: 'app-note-detail',
  standalone: true,
  imports: [LoadingSpinnerComponent, ErrorMessageComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './note-detail.component.html',
})
export class NoteDetailComponent {
  readonly note = input<NoteDetail | null>(null);
  readonly loading = input(false);
  readonly error = input<ApiError | null>(null);
  readonly isAdmin = input(false);

  readonly back = output<void>();
  readonly edit = output<void>();
  readonly publish = output<void>();
  readonly unpublish = output<void>();
  readonly delete = output<void>();
  readonly tagSelected = output<string>();

  readonly contentHtml = computed(() => {
    const note = this.note();
    if (!note?.content) return '';
    return renderMarkdown(note.content);
  });

  readonly isDraft = computed(() => this.note()?.publishStatus === 'Draft');
  readonly isPublished = computed(() => this.note()?.publishStatus === 'Published');

  noteDate(): string {
    const note = this.note();
    if (!note) return '';
    return formatDate(note.publishedAt ?? note.updatedAt);
  }
}

function renderMarkdown(markdown: string): string {
  const html = marked.parse(markdown, { async: false });
  const enhanced = html.replaceAll('<pre><code', '<pre class="markdown-code"><code');
  return DOMPurify.sanitize(enhanced);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('ru-RU', { dateStyle: 'medium' }).format(new Date(value));
}
