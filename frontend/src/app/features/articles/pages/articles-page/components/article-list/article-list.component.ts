import { ChangeDetectionStrategy, Component, computed, input, output } from '@angular/core';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { ArticleSummary } from '../../../../models/articles.model';

@Component({
  selector: 'app-article-list',
  standalone: true,
  imports: [TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './article-list.component.html',
})
export class ArticleListComponent {
  readonly articles = input.required<ArticleSummary[]>();
  readonly page = input.required<number>();
  readonly totalPages = input.required<number>();
  readonly dateLocale = input.required<string>();
  readonly canManageContent = input(false);

  readonly articleSelected = output<string>();
  readonly tagSelected = output<string>();
  readonly pageChange = output<number>();

  readonly hasPrevious = computed(() => this.page() > 1);
  readonly hasNext = computed(() => this.page() < this.totalPages());

  articleDate(article: ArticleSummary): string {
    return formatDate(article.publishedAt ?? article.updatedAt, this.dateLocale());
  }

  previousPage(): void {
    if (this.hasPrevious()) {
      this.pageChange.emit(this.page() - 1);
    }
  }

  nextPage(): void {
    if (this.hasNext()) {
      this.pageChange.emit(this.page() + 1);
    }
  }
}

function formatDate(value: string, locale: string): string {
  return new Intl.DateTimeFormat(locale, { dateStyle: 'medium' }).format(new Date(value));
}
