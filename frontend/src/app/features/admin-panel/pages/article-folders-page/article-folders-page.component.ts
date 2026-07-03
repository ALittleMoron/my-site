import { CdkDrag, CdkDragDrop, CdkDropList, moveItemInArray } from '@angular/cdk/drag-drop';
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
import { Observable } from 'rxjs';
import { ApiError } from '../../../../core/models/api-error.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { ArticleFolder } from '../../models/article-workspace.model';
import { ArticleWorkspaceService } from '../../services/article-workspace.service';

@Component({
  selector: 'app-article-folders-page',
  standalone: true,
  imports: [
    CdkDrag,
    CdkDropList,
    TranslatePipe,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './article-folders-page.component.html',
  styleUrl: './article-folders-page.component.scss',
})
export class ArticleFoldersPageComponent implements OnInit {
  private readonly articlesService = inject(ArticleWorkspaceService);
  private readonly notifications = inject(NotificationService);
  private readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);

  readonly folders = signal<ArticleFolder[]>([]);
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly isEmpty = computed(() => !this.loading() && this.folders().length === 0);

  ngOnInit(): void {
    this.loadFolders();
  }

  loadFolders(): void {
    this.loading.set(true);
    this.error.set(null);
    this.articlesService
      .getFolders(this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (folders) => {
          this.folders.set(folders);
          this.loading.set(false);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
          this.notifications.error(this.i18n.translate('articles.folders.loadError'));
        },
      });
  }

  dropFolders(event: CdkDragDrop<ArticleFolder[]>): void {
    this.reorderFolders(event.previousIndex, event.currentIndex);
  }

  private reorderFolders(previousIndex: number, currentIndex: number): void {
    const current = this.folders();
    if (this.shouldSkipReorder(previousIndex, currentIndex, current.length)) return;
    const snapshot = current.map((folder) => ({ ...folder }));
    const next = current.map((folder) => ({ ...folder }));
    moveItemInArray(next, previousIndex, currentIndex);
    renumberPriorities(next);
    this.folders.set(next);
    this.saveReorder(
      snapshot,
      this.articlesService.updateFolderPriorities(next.map((folder) => folder.id)),
    );
  }

  private saveReorder(snapshot: ArticleFolder[], request: Observable<void>): void {
    this.saving.set(true);
    request.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.saving.set(false);
        this.notifications.success(this.i18n.translate('articles.folders.saved'));
      },
      error: () => {
        this.folders.set(snapshot);
        this.saving.set(false);
        this.notifications.error(this.i18n.translate('articles.folders.saveError'));
        this.loadFolders();
      },
    });
  }

  private shouldSkipReorder(previousIndex: number, currentIndex: number, length: number): boolean {
    return (
      this.saving() ||
      previousIndex === currentIndex ||
      previousIndex < 0 ||
      currentIndex < 0 ||
      previousIndex >= length ||
      currentIndex >= length
    );
  }

  private currentLanguage(): 'ru' | 'en' {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }
}

function renumberPriorities(folders: ArticleFolder[]): void {
  folders.forEach((folder, index) => {
    folder.priority = index + 1;
  });
}
