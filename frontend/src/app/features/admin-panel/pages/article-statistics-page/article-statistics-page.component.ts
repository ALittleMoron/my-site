import { DOCUMENT } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { ApiError } from '../../../../core/models/api-error.model';
import { AdminArticleStats } from '../../models/article-workspace.model';
import { ArticleWorkspaceService } from '../../services/article-workspace.service';
import { AdminArticleStatisticsPanelComponent } from './components/article-statistics-panel/article-statistics-panel.component';

@Component({
  selector: 'app-admin-article-statistics-page',
  standalone: true,
  imports: [TranslatePipe, AdminArticleStatisticsPanelComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './article-statistics-page.component.html',
})
export class AdminArticleStatisticsPageComponent implements OnInit {
  private readonly articleWorkspace = inject(ArticleWorkspaceService);
  private readonly i18n = inject(I18nService);
  private readonly document = inject(DOCUMENT);
  private readonly destroyRef = inject(DestroyRef);

  readonly stats = signal<AdminArticleStats | null>(null);
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly dateFrom = signal(formatDateInput(daysBefore(new Date(), 30)));
  readonly dateTo = signal(formatDateInput(new Date()));

  readonly dateLocale = computed(() => this.i18n.dateLocale());
  readonly datePlaceholder = computed(() => {
    this.language();
    return this.i18n.translate('shared.datePicker.placeholder');
  });
  readonly openCalendarLabel = computed(() => {
    this.language();
    return this.i18n.translate('shared.datePicker.open');
  });
  readonly previousMonthLabel = computed(() => {
    this.language();
    return this.i18n.translate('shared.datePicker.previousMonth');
  });
  readonly nextMonthLabel = computed(() => {
    this.language();
    return this.i18n.translate('shared.datePicker.nextMonth');
  });
  readonly openMonthYearPickerLabel = computed(() => {
    this.language();
    return this.i18n.translate('shared.datePicker.openMonthYearPicker');
  });
  readonly previousYearLabel = computed(() => {
    this.language();
    return this.i18n.translate('shared.datePicker.previousYear');
  });
  readonly nextYearLabel = computed(() => {
    this.language();
    return this.i18n.translate('shared.datePicker.nextYear');
  });
  readonly language = computed(() => {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  });

  ngOnInit(): void {
    this.loadStats();
  }

  setDateFrom(value: string): void {
    this.dateFrom.set(value);
  }

  setDateTo(value: string): void {
    this.dateTo.set(value);
  }

  loadStats(): void {
    if (this.dateFrom().trim() === '' || this.dateTo().trim() === '') return;
    this.loading.set(true);
    this.error.set(null);
    this.articleWorkspace
      .getAdminStats({
        dateFrom: this.dateFrom(),
        dateTo: this.dateTo(),
        language: this.language(),
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (stats) => {
          this.stats.set(stats);
          this.loading.set(false);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
        },
      });
  }

  exportStatsCsv(): void {
    const stats = this.stats();
    const urlApi = this.document.defaultView?.URL;
    if (stats === null || urlApi === undefined) return;
    const csv = buildStatsCsv(stats);
    const url = urlApi.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const link = this.document.createElement('a');
    link.href = url;
    link.download = `articles-stats-${stats.dateFrom}-${stats.dateTo}.csv`;
    link.click();
    urlApi.revokeObjectURL(url);
  }
}

function daysBefore(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() - days);
  return result;
}

function formatDateInput(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function buildStatsCsv(stats: AdminArticleStats): string {
  const rows = [
    ['title', 'slug', 'views', 'engaged_views', 'heart', 'fire', 'thinking', 'neutral', 'poop'],
    ...stats.articles.map((article) => [
      article.title,
      article.slug,
      String(article.viewCount),
      String(article.engagedViewCount),
      String(article.reactionCounts.heart),
      String(article.reactionCounts.fire),
      String(article.reactionCounts.thinking),
      String(article.reactionCounts.neutral),
      String(article.reactionCounts.poop),
    ]),
  ];
  return rows.map((row) => row.map(escapeCsvCell).join(',')).join('\n');
}

function escapeCsvCell(value: string): string {
  return `"${value.replaceAll('"', '""')}"`;
}
