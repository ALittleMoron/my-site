import { Component, ChangeDetectionStrategy, input, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LanguageCode } from '../../../../../../core/i18n/i18n.model';
import { WikiLinkRendererService } from '../../../../../../core/wiki-links/wiki-link-renderer.service';
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
  private readonly wikiLinkRenderer = inject(WikiLinkRendererService);

  readonly question = input<MatrixQuestionDetail | null>(null);
  readonly loading = input<boolean>(false);
  readonly error = input<ApiError | null>(null);
  readonly language = input.required<LanguageCode>();
  readonly questionPageLink = input<string | null>(null);

  readonly answerHtml = computed<string>(() => {
    const q = this.question();
    if (!q?.answer) return '';
    return this.wikiLinkRenderer.render(q.answer, this.language());
  });

  readonly interviewAnswerHtml = computed<string>(() => {
    const q = this.question();
    if (!q?.interviewExpectedAnswer) return '';
    return this.wikiLinkRenderer.render(q.interviewExpectedAnswer, this.language());
  });

  readonly isPublished = computed<boolean>(() => this.question()?.publishStatus === 'Published');
  readonly canOpenQuestionPage = computed<boolean>(
    () => this.questionPageLink() !== null && this.isPublished(),
  );
}
