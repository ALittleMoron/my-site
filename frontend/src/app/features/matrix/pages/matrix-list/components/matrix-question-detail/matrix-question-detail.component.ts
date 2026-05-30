import { Component, ChangeDetectionStrategy, input, output, computed } from '@angular/core';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { MatrixQuestionDetail } from '../../../../models/matrix-question.model';
import { ApiError } from '../../../../../../core/models/api-error.model';
import { LoadingSpinnerComponent } from '../../../../../../shared/ui/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../../../../../shared/ui/error-message/error-message.component';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';

@Component({
  selector: 'app-matrix-question-detail',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [LoadingSpinnerComponent, ErrorMessageComponent, TranslatePipe],
  templateUrl: './matrix-question-detail.component.html',
})
export class MatrixQuestionDetailComponent {
  readonly question = input<MatrixQuestionDetail | null>(null);
  readonly loading = input<boolean>(false);
  readonly error = input<ApiError | null>(null);
  readonly isAdmin = input.required<boolean>();

  readonly publish = output<void>();
  readonly unpublish = output<void>();
  readonly delete = output<void>();
  readonly edit = output<void>();

  readonly answerHtml = computed<string>(() => {
    const q = this.question();
    if (!q?.answer) return '';
    return renderMarkdown(q.answer);
  });

  readonly interviewAnswerHtml = computed<string>(() => {
    const q = this.question();
    if (!q?.interviewExpectedAnswer) return '';
    return renderMarkdown(q.interviewExpectedAnswer);
  });

  readonly isDraft = computed<boolean>(() => this.question()?.publishStatus === 'Draft');
  readonly isPublished = computed<boolean>(() => this.question()?.publishStatus === 'Published');
}

function renderMarkdown(markdown: string): string {
  const html = marked.parse(markdown, { async: false });
  const enhanced = html.replaceAll('<pre><code', '<pre class="markdown-code"><code');
  return DOMPurify.sanitize(enhanced);
}
