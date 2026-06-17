import { DOCUMENT } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { ApiError } from '../../../../core/models/api-error.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import {
  AdminArticleDetail,
  AdminArticleList,
  AdminArticlePayload,
  AdminArticleTag,
  AdminArticleTree,
} from '../../models/article-workspace.model';
import { ArticleWorkspaceService } from '../../services/article-workspace.service';
import { ArticleFormComponent } from './components/article-form/article-form.component';

const PAGE_SIZE = 20;

@Component({
  selector: 'app-admin-articles-page',
  standalone: true,
  imports: [
    RouterLink,
    TranslatePipe,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
    ArticleFormComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './articles-page.component.html',
})
export class AdminArticlesPageComponent implements OnInit {
  private readonly articleWorkspace = inject(ArticleWorkspaceService);
  private readonly notifications = inject(NotificationService);
  private readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly document = inject(DOCUMENT);

  readonly page = signal(1);
  readonly searchQuery = signal('');
  readonly tagSlug = signal<string | null>(null);
  readonly publishedFrom = signal('');
  readonly publishedTo = signal('');
  readonly onlyPublished = signal(false);
  readonly articles = signal<AdminArticleList | null>(null);
  readonly tags = signal<AdminArticleTag[]>([]);
  readonly tree = signal<AdminArticleTree>({ folders: [] });
  readonly selectedArticle = signal<AdminArticleDetail | null>(null);
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly formVisible = signal(false);
  readonly formLoading = signal(false);
  readonly formError = signal<ApiError | null>(null);

  ngOnInit(): void {
    this.loadWorkspace();
    this.loadTags();
    this.loadTree();
  }

  loadWorkspace(): void {
    this.loading.set(true);
    this.error.set(null);
    this.articleWorkspace
      .listArticles({
        page: this.page(),
        pageSize: PAGE_SIZE,
        language: this.currentLanguage(),
        onlyPublished: this.onlyPublished(),
        tagSlug: this.tagSlug(),
        publishedFrom: this.publishedFrom() || null,
        publishedTo: this.publishedTo() || null,
        searchQuery: this.normalizedSearchQuery(),
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (articles) => {
          this.articles.set(articles);
          this.loading.set(false);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
          this.notifications.error(this.i18n.translate('adminArticlesWorkspace.loadError'));
        },
      });
  }

  applyFilters(): void {
    this.page.set(1);
    this.loadWorkspace();
  }

  resetFilters(): void {
    this.searchQuery.set('');
    this.tagSlug.set(null);
    this.publishedFrom.set('');
    this.publishedTo.set('');
    this.onlyPublished.set(false);
    this.page.set(1);
    this.loadWorkspace();
  }

  previousPage(): void {
    if (this.page() <= 1) return;
    this.page.update((page) => page - 1);
    this.loadWorkspace();
  }

  nextPage(): void {
    if (this.page() >= (this.articles()?.totalPages ?? 1)) return;
    this.page.update((page) => page + 1);
    this.loadWorkspace();
  }

  openCreate(): void {
    this.selectedArticle.set(null);
    this.formError.set(null);
    this.formLoading.set(false);
    this.formVisible.set(true);
  }

  openEdit(slug: string): void {
    this.selectedArticle.set(null);
    this.formError.set(null);
    this.formLoading.set(true);
    this.formVisible.set(true);
    this.articleWorkspace
      .getArticle(slug, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (article) => {
          this.selectedArticle.set(article);
          this.formLoading.set(false);
        },
        error: (err: ApiError) => {
          this.formError.set(err);
          this.formLoading.set(false);
        },
      });
  }

  closeForm(): void {
    this.formVisible.set(false);
    this.selectedArticle.set(null);
    this.formError.set(null);
    this.formLoading.set(false);
  }

  saveArticle(payload: AdminArticlePayload): void {
    const current = this.selectedArticle();
    const request =
      current === null
        ? this.articleWorkspace.createArticle(payload, this.currentLanguage())
        : this.articleWorkspace.updateArticle(current.slug, payload, this.currentLanguage());
    request.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.notifications.success(this.i18n.translate('articles.notify.saved'));
        this.closeForm();
        this.loadWorkspace();
        this.loadTags();
        this.loadTree();
      },
      error: (err: ApiError) => {
        this.formError.set(err);
        this.notifications.error(this.i18n.translate('articles.notify.saveError'));
      },
    });
  }

  publishArticle(slug: string): void {
    this.articleWorkspace
      .publishArticle(slug)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('articles.notify.published'));
          this.loadWorkspace();
          this.loadTree();
        },
        error: () => this.notifications.error(this.i18n.translate('articles.notify.publishError')),
      });
  }

  unpublishArticle(slug: string): void {
    this.articleWorkspace
      .unpublishArticle(slug)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('articles.notify.unpublished'));
          this.loadWorkspace();
          this.loadTree();
        },
        error: () =>
          this.notifications.error(this.i18n.translate('articles.notify.unpublishError')),
      });
  }

  deleteArticle(slug: string): void {
    if (
      this.document.defaultView?.confirm(
        this.i18n.translate('adminArticlesWorkspace.confirmDelete'),
      ) !== true
    ) {
      return;
    }
    this.articleWorkspace
      .deleteArticle(slug)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('articles.notify.deleted'));
          this.loadWorkspace();
          this.loadTree();
        },
        error: () => this.notifications.error(this.i18n.translate('articles.notify.deleteError')),
      });
  }

  setSearchQuery(value: string): void {
    this.searchQuery.set(value);
  }

  setTagSlug(value: string): void {
    this.tagSlug.set(value === '' ? null : value);
  }

  setPublishedFrom(value: string): void {
    this.publishedFrom.set(value);
  }

  setPublishedTo(value: string): void {
    this.publishedTo.set(value);
  }

  setOnlyPublished(value: boolean): void {
    this.onlyPublished.set(value);
  }

  publicArticleLink(slug: string): string {
    return `/${this.currentLanguage()}/articles/${slug}`;
  }

  loadTags(): void {
    this.articleWorkspace
      .getTags(false, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tags) => this.tags.set(tags),
        error: () => this.tags.set([]),
      });
  }

  private loadTree(): void {
    this.articleWorkspace
      .getTree(this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tree) => this.tree.set(tree),
        error: () => this.tree.set({ folders: [] }),
      });
  }

  private normalizedSearchQuery(): string | null {
    const value = this.searchQuery().trim();
    return value === '' ? null : value;
  }

  private currentLanguage(): 'ru' | 'en' {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }
}
