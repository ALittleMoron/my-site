import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
  computed,
  DestroyRef,
  OnInit,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MatrixService } from '../../services/matrix.service';
import {
  MatrixQuestionDetail,
  MatrixQuestionList,
} from '../../models/matrix-question.model';
import { ApiError } from '../../../../core/models/api-error.model';
import { AuthService } from '../../../../core/auth/auth.service';
import {
  LayoutPreferencesService,
  MatrixLayoutMode,
} from '../../../../core/layout/layout-preferences.service';
import { SeoService } from '../../../../core/seo/seo.service';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { MatrixSheetTabsComponent } from './components/matrix-sheet-tabs/matrix-sheet-tabs.component';
import { MatrixFilterBarComponent } from './components/matrix-filter-bar/matrix-filter-bar.component';
import { MatrixGroupedListComponent } from './components/matrix-grouped-list/matrix-grouped-list.component';
import { MatrixGroupedGridComponent } from './components/matrix-grouped-grid/matrix-grouped-grid.component';
import { MatrixQuestionDetailComponent } from './components/matrix-question-detail/matrix-question-detail.component';

const CHOSEN_SHEET_KEY = 'chosenSheet';

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
  ],
  templateUrl: './matrix-list.component.html',
  styleUrl: './matrix-list.component.scss',
})
export class MatrixListComponent implements OnInit {
  private readonly matrixService = inject(MatrixService);
  private readonly authService = inject(AuthService);
  private readonly layoutPreferences = inject(LayoutPreferencesService);
  private readonly seoService = inject(SeoService);
  private readonly destroyRef = inject(DestroyRef);

  readonly isAdmin = this.authService.isAdmin;

  readonly sheets = signal<string[]>([]);
  readonly selectedSheet = signal<string | null>(null);
  readonly questions = signal<MatrixQuestionList | null>(null);
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly search = signal('');
  readonly onlyPublished = signal(true);
  readonly selectedQuestion = signal<MatrixQuestionDetail | null>(null);
  readonly detailLoading = signal(false);
  readonly detailError = signal<ApiError | null>(null);
  readonly detailVisible = signal(false);

  readonly layoutMode = this.layoutPreferences.matrixLayout;

  readonly filteredQuestions = computed<MatrixQuestionList | null>(() => {
    const list = this.questions();
    if (!list) return null;
    const term = this.search().toLowerCase().trim();
    if (!term) return list;

    const sections = list.sections
      .map(section => ({
        ...section,
        subsections: section.subsections
          .map(subsection => ({
            ...subsection,
            grades: subsection.grades
              .map(grade => ({
                ...grade,
                questions: grade.questions.filter(q =>
                  q.question.toLowerCase().includes(term),
                ),
              }))
              .filter(grade => grade.questions.length > 0),
          }))
          .filter(subsection => subsection.grades.length > 0),
      }))
      .filter(section => section.subsections.length > 0);

    return { ...list, sections };
  });

  readonly isEmpty = computed(
    () =>
      !this.loading() &&
      !this.error() &&
      (this.filteredQuestions()?.sections.length ?? 0) === 0,
  );

  ngOnInit(): void {
    this.seoService.setMeta({
      title: 'Матрица компетенций',
      description: 'Матрица компетенций Junior/Middle/Senior разработчика.',
    });
    this.loadSheets();
  }

  loadSheets(): void {
    this.loading.set(true);
    this.error.set(null);
    this.matrixService
      .getSheets()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: sheets => {
          this.sheets.set(sheets);
          if (sheets.length > 0) {
            const saved = localStorage.getItem(CHOSEN_SHEET_KEY);
            const initial =
              saved && sheets.includes(saved) ? saved : sheets[0];
            this.selectedSheet.set(initial);
            this.loadQuestions(initial);
          } else {
            this.loading.set(false);
          }
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
        },
      });
  }

  loadQuestions(sheetName: string): void {
    this.loading.set(true);
    this.error.set(null);
    this.matrixService
      .getQuestions(sheetName, this.onlyPublished())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: list => {
          this.questions.set(list);
          this.loading.set(false);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
        },
      });
  }

  selectSheet(sheetName: string): void {
    this.selectedSheet.set(sheetName);
    localStorage.setItem(CHOSEN_SHEET_KEY, sheetName);
    this.loadQuestions(sheetName);
  }

  setSearch(value: string): void {
    this.search.set(value);
  }

  setOnlyPublished(value: boolean): void {
    this.onlyPublished.set(value);
    const sheet = this.selectedSheet();
    if (sheet) {
      this.loadQuestions(sheet);
    }
  }

  setLayoutMode(mode: MatrixLayoutMode): void {
    this.layoutPreferences.setMatrixLayout(mode);
  }

  openDetail(id: number): void {
    this.detailVisible.set(true);
    this.selectedQuestion.set(null);
    this.detailLoading.set(true);
    this.detailError.set(null);
    this.matrixService
      .getQuestion(id, this.onlyPublished())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: detail => {
          this.selectedQuestion.set(detail);
          this.detailLoading.set(false);
        },
        error: (err: ApiError) => {
          this.detailError.set(err);
          this.detailLoading.set(false);
        },
      });
  }

  closeDetail(): void {
    this.detailVisible.set(false);
    this.selectedQuestion.set(null);
    this.detailError.set(null);
  }

  onPublish(id: number): void {
    this.matrixService
      .publishQuestion(id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          const sheet = this.selectedSheet();
          if (sheet) this.loadQuestions(sheet);
        },
        error: (err: ApiError) => {
          this.error.set(err);
        },
      });
  }

  onUnpublish(id: number): void {
    this.matrixService
      .unpublishQuestion(id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          const sheet = this.selectedSheet();
          if (sheet) this.loadQuestions(sheet);
        },
        error: (err: ApiError) => {
          this.error.set(err);
        },
      });
  }

  onDelete(id: number): void {
    this.matrixService
      .deleteQuestion(id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.closeDetail();
          const sheet = this.selectedSheet();
          if (sheet) this.loadQuestions(sheet);
        },
        error: (err: ApiError) => {
          this.error.set(err);
        },
      });
  }
}
