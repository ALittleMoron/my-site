import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
  computed,
  effect,
  untracked,
  DestroyRef,
  OnInit,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EMPTY, Subject, catchError, debounceTime, distinctUntilChanged, switchMap } from 'rxjs';
import { MatrixService } from '../../services/matrix.service';
import {
  MatrixQuestionDetail,
  MatrixQuestionList,
  MatrixQuestionPayload,
  MatrixResource,
  MatrixSheet,
} from '../../models/matrix-question.model';
import { ApiError } from '../../../../core/models/api-error.model';
import { AuthService } from '../../../../core/auth/auth.service';
import {
  LayoutPreferencesService,
  MatrixLayoutMode,
} from '../../../../core/layout/layout-preferences.service';
import { SeoService } from '../../../../core/seo/seo.service';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { LanguageCode } from '../../../../core/i18n/i18n.model';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { MatrixSheetTabsComponent } from './components/matrix-sheet-tabs/matrix-sheet-tabs.component';
import { MatrixFilterBarComponent } from './components/matrix-filter-bar/matrix-filter-bar.component';
import { MatrixGroupedListComponent } from './components/matrix-grouped-list/matrix-grouped-list.component';
import { MatrixGroupedGridComponent } from './components/matrix-grouped-grid/matrix-grouped-grid.component';
import { MatrixQuestionDetailComponent } from './components/matrix-question-detail/matrix-question-detail.component';
import { MatrixQuestionFormComponent } from './components/matrix-question-form/matrix-question-form.component';

const CHOSEN_SHEET_KEY = 'chosenSheet';
const RESOURCE_SEARCH_LIMIT = 10;

@Component({
  selector: 'app-matrix-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
    MatrixSheetTabsComponent,
    MatrixFilterBarComponent,
    MatrixGroupedListComponent,
    MatrixGroupedGridComponent,
    MatrixQuestionDetailComponent,
    MatrixQuestionFormComponent,
    TranslatePipe,
  ],
  templateUrl: './matrix-list.component.html',
  styleUrl: './matrix-list.component.scss',
})
export class MatrixListComponent implements OnInit {
  private readonly matrixService = inject(MatrixService);
  private readonly authService = inject(AuthService);
  private readonly layoutPreferences = inject(LayoutPreferencesService);
  private readonly seoService = inject(SeoService);
  private readonly notifications = inject(NotificationService);
  private readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly resourceSearchTerm = new Subject<string>();
  private languageReloadInitialized = false;

  readonly isAdmin = this.authService.isAdmin;

  readonly sheets = signal<MatrixSheet[]>([]);
  readonly selectedSheetKey = signal<string | null>(null);
  readonly questions = signal<MatrixQuestionList | null>(null);
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly search = signal('');
  readonly onlyPublished = signal(true);
  readonly selectedQuestion = signal<MatrixQuestionDetail | null>(null);
  readonly detailLoading = signal(false);
  readonly detailError = signal<ApiError | null>(null);
  readonly detailVisible = signal(false);
  readonly detailMode = signal<'view' | 'edit' | 'create'>('view');
  readonly resourceSearchResults = signal<MatrixResource[]>([]);

  readonly layoutMode = this.layoutPreferences.matrixLayout;
  readonly selectedSheet = computed<MatrixSheet | null>(() => {
    const selectedSheetKey = this.selectedSheetKey();
    if (selectedSheetKey === null) return null;
    return this.sheets().find((sheet) => sheet.key === selectedSheetKey) ?? null;
  });

  readonly filteredQuestions = computed<MatrixQuestionList | null>(() => {
    const list = this.questions();
    if (!list) return null;
    const term = this.search().toLowerCase().trim();
    if (!term) return list;

    const sections = list.sections
      .map((section) => ({
        ...section,
        subsections: section.subsections
          .map((subsection) => ({
            ...subsection,
            grades: subsection.grades
              .map((grade) => ({
                ...grade,
                questions: grade.questions.filter((q) => q.question.toLowerCase().includes(term)),
              }))
              .filter((grade) => grade.questions.length > 0),
          }))
          .filter((subsection) => subsection.grades.length > 0),
      }))
      .filter((section) => section.subsections.length > 0);

    return { ...list, sections };
  });

  readonly isEmpty = computed(
    () =>
      !this.loading() && !this.error() && (this.filteredQuestions()?.sections.length ?? 0) === 0,
  );

  private readonly languageReloadEffect = effect(() => {
    const language = this.i18n.language();
    if (language === null) return;
    if (!this.languageReloadInitialized) {
      this.languageReloadInitialized = true;
      return;
    }
    untracked(() => this.reloadLocalizedContent());
  });

  ngOnInit(): void {
    this.seoService.setTranslatedMeta({
      titleKey: 'matrix.seo.title',
      descriptionKey: 'matrix.seo.description',
      canonicalPath: '/competency-matrix',
    });
    this.loadSheets();
    this.resourceSearchTerm
      .pipe(
        debounceTime(250),
        distinctUntilChanged(),
        switchMap((searchName) => {
          const trimmedSearchName = searchName.trim();
          if (trimmedSearchName.length < 2) {
            this.resourceSearchResults.set([]);
            return EMPTY;
          }
          return this.matrixService
            .searchResources(trimmedSearchName, RESOURCE_SEARCH_LIMIT, this.currentLanguage())
            .pipe(
              catchError(() => {
                this.resourceSearchResults.set([]);
                this.notifications.error(this.i18n.translate('matrix.notify.resourcesError'));
                return EMPTY;
              }),
            );
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((resources) => this.resourceSearchResults.set(resources));
  }

  loadSheets(): void {
    this.loading.set(true);
    this.error.set(null);
    this.matrixService
      .getSheets(this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (sheets) => {
          this.sheets.set(sheets);
          if (sheets.length > 0) {
            const saved = localStorage.getItem(CHOSEN_SHEET_KEY);
            const initial =
              saved && sheets.some((sheet) => sheet.key === saved) ? saved : sheets[0].key;
            this.selectedSheetKey.set(initial);
            this.loadQuestions(initial);
          } else {
            this.selectedSheetKey.set(null);
            this.questions.set(null);
            this.loading.set(false);
          }
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
        },
      });
  }

  loadQuestions(sheetKey: string): void {
    this.loading.set(true);
    this.error.set(null);
    this.matrixService
      .getQuestions(sheetKey, this.onlyPublished(), this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (list) => {
          this.questions.set(list);
          this.loading.set(false);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
        },
      });
  }

  selectSheet(sheetKey: string): void {
    this.selectedSheetKey.set(sheetKey);
    localStorage.setItem(CHOSEN_SHEET_KEY, sheetKey);
    this.loadQuestions(sheetKey);
  }

  setSearch(value: string): void {
    this.search.set(value);
  }

  setOnlyPublished(value: boolean): void {
    this.onlyPublished.set(value);
    const sheetKey = this.selectedSheetKey();
    if (sheetKey) {
      this.loadQuestions(sheetKey);
    }
  }

  setLayoutMode(mode: MatrixLayoutMode): void {
    this.layoutPreferences.setMatrixLayout(mode);
  }

  openDetail(id: number): void {
    this.detailVisible.set(true);
    this.detailMode.set('view');
    this.selectedQuestion.set(null);
    this.detailLoading.set(true);
    this.detailError.set(null);
    this.matrixService
      .getQuestion(id, this.onlyPublished(), this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (detail) => {
          this.selectedQuestion.set(detail);
          this.detailLoading.set(false);
        },
        error: (err: ApiError) => {
          this.detailError.set(err);
          this.detailLoading.set(false);
        },
      });
  }

  openCreate(): void {
    this.detailVisible.set(true);
    this.detailMode.set('create');
    this.selectedQuestion.set(null);
    this.detailError.set(null);
    this.detailLoading.set(false);
    this.resourceSearchResults.set([]);
  }

  openEdit(): void {
    this.detailMode.set('edit');
    this.resourceSearchResults.set([]);
  }

  closeDetail(): void {
    this.detailVisible.set(false);
    this.selectedQuestion.set(null);
    this.detailError.set(null);
    this.detailMode.set('view');
    this.resourceSearchResults.set([]);
  }

  searchResources(searchName: string): void {
    this.resourceSearchTerm.next(searchName);
  }

  saveQuestion(payload: MatrixQuestionPayload): void {
    const current = this.selectedQuestion();
    const request =
      this.detailMode() === 'edit' && current
        ? this.matrixService.updateQuestion(current.id, payload, this.currentLanguage())
        : this.matrixService.createQuestion(payload, this.currentLanguage());
    request.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (detail) => {
        this.selectedQuestion.set(detail);
        this.detailMode.set('view');
        this.notifications.success(this.i18n.translate('matrix.notify.saved'));
        this.selectedSheetKey.set(detail.sheetKey);
        localStorage.setItem(CHOSEN_SHEET_KEY, detail.sheetKey);
        this.loadQuestions(detail.sheetKey);
      },
      error: (err: ApiError) => {
        this.detailError.set(err);
        this.notifications.error(this.i18n.translate('matrix.notify.saveError'));
      },
    });
  }

  onPublish(id: number): void {
    this.matrixService
      .publishQuestion(id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('matrix.notify.published'));
          const sheetKey = this.selectedSheetKey();
          if (sheetKey) this.loadQuestions(sheetKey);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.notifications.error(this.i18n.translate('matrix.notify.publishError'));
        },
      });
  }

  onUnpublish(id: number): void {
    this.matrixService
      .unpublishQuestion(id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('matrix.notify.unpublished'));
          const sheetKey = this.selectedSheetKey();
          if (sheetKey) this.loadQuestions(sheetKey);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.notifications.error(this.i18n.translate('matrix.notify.unpublishError'));
        },
      });
  }

  onDelete(id: number): void {
    this.matrixService
      .deleteQuestion(id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('matrix.notify.deleted'));
          this.closeDetail();
          const sheetKey = this.selectedSheetKey();
          if (sheetKey) this.loadQuestions(sheetKey);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.notifications.error(this.i18n.translate('matrix.notify.deleteError'));
        },
      });
  }

  private reloadLocalizedContent(): void {
    this.loadSheets();
    const detail = this.selectedQuestion();
    if (detail !== null && this.detailVisible() && this.detailMode() === 'view') {
      this.openDetail(detail.id);
    }
  }

  private currentLanguage(): LanguageCode {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }
}
