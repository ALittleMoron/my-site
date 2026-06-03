import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  computed,
  inject,
  SecurityContext,
} from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { RouterLink } from '@angular/router';
import { marked } from 'marked';
import { MatrixQuestionDetail } from '../../../../models/matrix-question.model';
import { ApiError } from '../../../../../../core/models/api-error.model';
import { LoadingSpinnerComponent } from '../../../../../../shared/ui/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../../../../../shared/ui/error-message/error-message.component';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';

@Component({
  selector: 'app-matrix-question-detail',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, LoadingSpinnerComponent, ErrorMessageComponent, TranslatePipe],
  templateUrl: './matrix-question-detail.component.html',
})
export class MatrixQuestionDetailComponent {
  private readonly sanitizer = inject(DomSanitizer);

  readonly question = input<MatrixQuestionDetail | null>(null);
  readonly loading = input<boolean>(false);
  readonly error = input<ApiError | null>(null);
  readonly isAdmin = input.required<boolean>();
  readonly questionPageLink = input<string | null>(null);

  readonly publish = output<void>();
  readonly unpublish = output<void>();
  readonly delete = output<void>();
  readonly edit = output<void>();

  readonly answerHtml = computed<string>(() => {
    const q = this.question();
    if (!q?.answer) return '';
    return renderMarkdown(q.answer, this.sanitizer);
  });

  readonly interviewAnswerHtml = computed<string>(() => {
    const q = this.question();
    if (!q?.interviewExpectedAnswer) return '';
    return renderMarkdown(q.interviewExpectedAnswer, this.sanitizer);
  });

  readonly isDraft = computed<boolean>(() => this.question()?.publishStatus === 'Draft');
  readonly isPublished = computed<boolean>(() => this.question()?.publishStatus === 'Published');
  readonly canOpenQuestionPage = computed<boolean>(
    () => this.questionPageLink() !== null && this.isPublished(),
  );
}

function renderMarkdown(markdown: string, sanitizer: DomSanitizer): string {
  const html = marked.parse(markdown, { async: false });
  const enhanced = html.replaceAll('<pre><code', '<pre class="markdown-code"><code');
  return sanitizer.sanitize(SecurityContext.HTML, enhanced) ?? '';
}
