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
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiError } from '../../../../core/models/api-error.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { MatrixGroupedGridComponent } from '../../../../shared/ui/matrix-grouped-grid/matrix-grouped-grid.component';
import { MatrixSheetTabsComponent } from '../../../../shared/ui/matrix-sheet-tabs/matrix-sheet-tabs.component';
import {
  AdminAction,
  AdminActionsDropdownComponent,
} from '../../components/admin-actions-dropdown/admin-actions-dropdown.component';
import { MatrixQuestionFormComponent } from '../../components/matrix-question-form/matrix-question-form.component';
import {
  AdminMatrixGrade,
  AdminMatrixInterviewFrequency,
  AdminMatrixMissingField,
  AdminMatrixPublishStatus,
  AdminMatrixQuestionPayload,
  AdminMatrixQuestionWorkspace,
  AdminMatrixQuestionWorkspaceFilters,
  AdminMatrixWorkspaceFilterOptions,
  AdminMatrixWorkspaceItem,
  AdminMatrixWorkspaceSort,
  AdminReadonlyMatrixQuestionList,
  AdminReadonlyMatrixSheet,
} from '../../models/matrix-question-workspace.model';
import { MatrixQuestionWorkspaceService } from '../../services/matrix-question-workspace.service';

const GRADES: readonly AdminMatrixGrade[] = ['Junior', 'Junior+', 'Middle', 'Middle+', 'Senior'];
const SORTS: readonly AdminMatrixWorkspaceSort[] = [
  'newest',
  'oldest',
  'grade',
  'interviewFrequency',
  'section',
  'subsection',
  'missingFields',
  'dangerousPublished',
];
const PAGE_SIZES: readonly number[] = [20, 50, 100];

type WorkspaceTab = 'list' | 'preview';

@Component({
  selector: 'app-matrix-questions-page',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    TranslatePipe,
    RouterLink,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
    MatrixSheetTabsComponent,
    MatrixGroupedGridComponent,
    AdminActionsDropdownComponent,
    MatrixQuestionFormComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-questions-page.component.html',
  styleUrl: './matrix-questions-page.component.scss',
})
export class MatrixQuestionsPageComponent implements OnInit {
  private readonly workspaceService = inject(MatrixQuestionWorkspaceService);
  private readonly notifications = inject(NotificationService);
  private readonly i18n = inject(I18nService);
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);
  private readonly document = inject(DOCUMENT);
  private readonly router = inject(Router);

  readonly grades = GRADES;
  readonly sorts = SORTS;
  readonly pageSizes = PAGE_SIZES;

  readonly activeTab = signal<WorkspaceTab>('list');
  readonly workspace = signal<AdminMatrixQuestionWorkspace | null>(null);
  readonly filterOptions = signal<AdminMatrixWorkspaceFilterOptions>({
    sheets: [],
    grades: [],
    interviewFrequencies: [],
    sections: [],
    subsections: [],
    publishStatuses: [],
  });
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly page = signal(1);
  readonly selectedFilterSheetKey = signal('');
  readonly selectedFilterSection = signal('');

  readonly previewSheets = signal<AdminReadonlyMatrixSheet[]>([]);
  readonly selectedPreviewSheetKey = signal<string | null>(null);
  readonly previewQuestions = signal<AdminReadonlyMatrixQuestionList | null>(null);
  readonly previewLoading = signal(false);
  readonly previewError = signal<ApiError | null>(null);
  readonly previewLoaded = signal(false);

  readonly formMode = signal<'create' | null>(null);
  readonly formSubmitting = signal(false);
  readonly formError = signal<ApiError | null>(null);

  readonly filtersForm = this.formBuilder.group({
    searchQuery: [''],
    sheetKey: [''],
    grade: [''],
    interviewFrequency: [''],
    section: [''],
    subsection: [''],
    publishStatus: [''],
    publishedFrom: [''],
    publishedTo: [''],
    hasMissingFields: [''],
    sort: this.formBuilder.control<AdminMatrixWorkspaceSort>('newest', {
      validators: Validators.required,
    }),
    pageSize: this.formBuilder.control('20', { validators: Validators.required }),
  });

  readonly isEmpty = computed(() => !this.loading() && (this.workspace()?.items.length ?? 0) === 0);
  readonly canGoBack = computed(() => this.page() > 1);
  readonly canGoForward = computed(() => this.page() < (this.workspace()?.totalPages ?? 1));
  readonly sectionOptions = computed(() => {
    const sheetKey = this.selectedFilterSheetKey();
    if (!sheetKey) return [];
    return this.filterOptions().sheets.find((sheet) => sheet.key === sheetKey)?.sections ?? [];
  });
  readonly subsectionOptions = computed(() => {
    const section = this.selectedFilterSection();
    if (!section) return [];
    return this.sectionOptions().find((option) => option.label === section)?.subsections ?? [];
  });
  readonly readonlyMatrixLabels = computed(() => {
    this.i18n.language();
    return {
      sheetTabsAria: this.i18n.translate('matrix.grid.sheetsAria'),
      section: this.i18n.translate('matrix.grid.section'),
      subsection: this.i18n.translate('matrix.grid.subsection'),
      notSet: this.i18n.translate('shared.notSet'),
      grades: Object.fromEntries(
        GRADES.map((grade) => [grade, this.i18n.translate(this.i18n.enumGradeKey(grade))]),
      ),
    };
  });

  ngOnInit(): void {
    this.setupDependentFilters();
    this.loadFilterOptions();
    this.loadWorkspace();
  }

  private setupDependentFilters(): void {
    this.filtersForm.controls.section.disable({ emitEvent: false });
    this.filtersForm.controls.subsection.disable({ emitEvent: false });
    this.filtersForm.controls.sheetKey.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((sheetKey) => {
        this.selectedFilterSheetKey.set(sheetKey);
        this.selectedFilterSection.set('');
        this.filtersForm.controls.section.setValue('', { emitEvent: false });
        this.filtersForm.controls.subsection.setValue('', { emitEvent: false });
        this.refreshDependentFilterControls();
      });
    this.filtersForm.controls.section.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((section) => {
        this.selectedFilterSection.set(section);
        this.filtersForm.controls.subsection.setValue('', { emitEvent: false });
        this.refreshDependentFilterControls();
      });
  }

  switchTab(tab: WorkspaceTab): void {
    this.activeTab.set(tab);
    if (tab === 'preview' && !this.previewLoaded()) {
      this.loadPreviewSheets();
    }
  }

  loadFilterOptions(): void {
    this.workspaceService
      .getFilterOptions(this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (options) => {
          this.filterOptions.set(options);
          this.refreshDependentFilterControls();
        },
        error: () =>
          this.notifications.error(this.i18n.translate('adminMatrixWorkspace.optionsError')),
      });
  }

  loadWorkspace(): void {
    this.loading.set(true);
    this.error.set(null);
    this.workspaceService
      .listWorkspaceItems(this.buildWorkspaceFilters())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (workspace) => {
          this.workspace.set(workspace);
          this.loading.set(false);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
          this.notifications.error(this.i18n.translate('adminMatrixWorkspace.loadError'));
        },
      });
  }

  applyFilters(): void {
    this.page.set(1);
    this.loadWorkspace();
  }

  resetFilters(): void {
    this.filtersForm.reset({
      searchQuery: '',
      sheetKey: '',
      grade: '',
      interviewFrequency: '',
      section: '',
      subsection: '',
      publishStatus: '',
      publishedFrom: '',
      publishedTo: '',
      hasMissingFields: '',
      sort: 'newest',
      pageSize: '20',
    });
    this.page.set(1);
    this.loadWorkspace();
  }

  previousPage(): void {
    if (!this.canGoBack()) return;
    this.page.update((value) => value - 1);
    this.loadWorkspace();
  }

  nextPage(): void {
    if (!this.canGoForward()) return;
    this.page.update((value) => value + 1);
    this.loadWorkspace();
  }

  loadPreviewSheets(): void {
    this.previewLoading.set(true);
    this.previewError.set(null);
    this.workspaceService
      .listPublicPreviewSheets(this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (sheets) => {
          this.previewSheets.set(sheets);
          this.previewLoaded.set(true);
          const firstSheet = sheets[0] ?? null;
          this.selectedPreviewSheetKey.set(firstSheet?.key ?? null);
          if (firstSheet) {
            this.loadPreviewQuestions(firstSheet.key);
          } else {
            this.previewQuestions.set(null);
            this.previewLoading.set(false);
          }
        },
        error: (err: ApiError) => {
          this.previewError.set(err);
          this.previewLoading.set(false);
        },
      });
  }

  selectPreviewSheet(sheetKey: string): void {
    this.selectedPreviewSheetKey.set(sheetKey);
    this.loadPreviewQuestions(sheetKey);
  }

  loadPreviewQuestions(sheetKey: string): void {
    this.previewLoading.set(true);
    this.previewError.set(null);
    this.workspaceService
      .listPublicPreviewQuestions(sheetKey, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (questions) => {
          this.previewQuestions.set(questions);
          this.previewLoading.set(false);
        },
        error: (err: ApiError) => {
          this.previewError.set(err);
          this.previewLoading.set(false);
        },
      });
  }

  openCreate(): void {
    this.formMode.set('create');
    this.formError.set(null);
    this.formSubmitting.set(false);
  }

  closeForm(): void {
    if (this.formSubmitting()) return;
    this.formMode.set(null);
    this.formError.set(null);
  }

  saveQuestion(payload: AdminMatrixQuestionPayload): void {
    this.formSubmitting.set(true);
    this.formError.set(null);
    this.workspaceService
      .createQuestion(payload, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.formSubmitting.set(false);
          this.closeForm();
          this.notifications.success(this.i18n.translate('adminMatrixWorkspace.saved'));
          this.loadFilterOptions();
          this.loadWorkspace();
        },
        error: (err: ApiError) => {
          this.formError.set(err);
          this.formSubmitting.set(false);
          this.notifications.error(this.i18n.translate('adminMatrixWorkspace.saveError'));
        },
      });
  }

  publish(item: AdminMatrixWorkspaceItem): void {
    if (item.missingFields.length > 0) {
      this.notifications.error(
        this.i18n.translate('adminMatrixWorkspace.publishMissingFields', {
          fields: this.missingFieldsText(item.missingFields),
        }),
      );
      return;
    }
    this.workspaceService
      .publishQuestion(item.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('matrix.notify.published'));
          this.loadWorkspace();
        },
        error: () => this.notifications.error(this.i18n.translate('matrix.notify.publishError')),
      });
  }

  unpublish(item: AdminMatrixWorkspaceItem): void {
    this.workspaceService
      .unpublishQuestion(item.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('matrix.notify.unpublished'));
          this.loadWorkspace();
        },
        error: () => this.notifications.error(this.i18n.translate('matrix.notify.unpublishError')),
      });
  }

  delete(item: AdminMatrixWorkspaceItem): void {
    if (
      this.document.defaultView?.confirm(
        this.i18n.translate('adminMatrixWorkspace.confirmDelete'),
      ) !== true
    ) {
      return;
    }
    this.workspaceService
      .deleteQuestion(item.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('matrix.notify.deleted'));
          this.loadWorkspace();
        },
        error: () => this.notifications.error(this.i18n.translate('matrix.notify.deleteError')),
      });
  }

  matrixActions(item: AdminMatrixWorkspaceItem): AdminAction[] {
    const publicationAction =
      item.publishStatus === 'Published'
        ? {
            id: 'unpublish',
            label: this.i18n.translate('shared.unpublish'),
            destructive: false,
            disabled: false,
          }
        : {
            id: 'publish',
            label: this.i18n.translate('shared.publish'),
            destructive: false,
            disabled: false,
          };
    return [
      {
        id: 'edit',
        label: this.i18n.translate('shared.edit'),
        destructive: false,
        disabled: false,
      },
      publicationAction,
      {
        id: 'delete',
        label: this.i18n.translate('shared.delete'),
        destructive: true,
        disabled: false,
      },
    ];
  }

  handleMatrixAction(actionId: string, item: AdminMatrixWorkspaceItem): void {
    switch (actionId) {
      case 'edit':
        void this.router.navigate(['/admin-panel/matrix-questions', item.id]);
        return;
      case 'publish':
        this.publish(item);
        return;
      case 'unpublish':
        this.unpublish(item);
        return;
      case 'delete':
        this.delete(item);
        return;
      default:
        throw new Error(`Unsupported matrix question action: ${actionId}`);
    }
  }

  gradeLabel(grade: AdminMatrixGrade | null): string {
    return grade === null
      ? this.i18n.translate('shared.notSet')
      : this.i18n.translate(this.i18n.enumGradeKey(grade));
  }

  interviewFrequencyLabel(frequency: AdminMatrixInterviewFrequency | null): string {
    return frequency === null
      ? this.i18n.translate('shared.notSet')
      : this.i18n.translate(this.i18n.enumInterviewFrequencyKey(frequency));
  }

  sortLabel(sort: AdminMatrixWorkspaceSort): string {
    return this.i18n.translate(`adminMatrixWorkspace.sort.${sort}`);
  }

  publishStatusLabel(status: AdminMatrixPublishStatus): string {
    return this.i18n.translate(`enum.publishStatus.${status}`);
  }

  missingFieldLabel(field: string): string {
    return this.i18n.translate(`adminMatrixWorkspace.missing.${field}`);
  }

  missingFieldsText(fields: readonly AdminMatrixMissingField[]): string {
    return fields.map((field) => this.missingFieldLabel(field)).join(', ');
  }

  isPublicReady(item: AdminMatrixWorkspaceItem): boolean {
    return item.publishStatus === 'Published' && item.missingFields.length === 0;
  }

  publicQuestionLink(item: AdminMatrixWorkspaceItem): string {
    return `/${this.currentLanguage()}/competency-matrix/questions/${item.slug}`;
  }

  private buildWorkspaceFilters(): AdminMatrixQuestionWorkspaceFilters {
    const raw = this.filtersForm.getRawValue();
    return {
      page: this.page(),
      pageSize: Number(raw.pageSize),
      language: this.currentLanguage(),
      sort: raw.sort,
      searchQuery: normalizedValue(raw.searchQuery),
      sheetKeys: singleValueArray(raw.sheetKey),
      grades: singleValueArray(raw.grade) as AdminMatrixGrade[],
      interviewFrequencies: singleValueArray(raw.interviewFrequency) as
        AdminMatrixInterviewFrequency[] | undefined,
      sections: singleValueArray(raw.section),
      subsections: singleValueArray(raw.subsection),
      publishStatuses: singleValueArray(raw.publishStatus) as AdminMatrixPublishStatus[],
      publishedFrom: normalizedValue(raw.publishedFrom),
      publishedTo: normalizedValue(raw.publishedTo),
      hasMissingFields: raw.hasMissingFields === '' ? undefined : raw.hasMissingFields === 'true',
    };
  }

  private refreshDependentFilterControls(): void {
    if (this.selectedFilterSheetKey() && this.sectionOptions().length > 0) {
      this.filtersForm.controls.section.enable({ emitEvent: false });
    } else {
      this.filtersForm.controls.section.disable({ emitEvent: false });
    }

    if (this.selectedFilterSection() && this.subsectionOptions().length > 0) {
      this.filtersForm.controls.subsection.enable({ emitEvent: false });
    } else {
      this.filtersForm.controls.subsection.disable({ emitEvent: false });
    }
  }

  currentLanguage(): 'ru' | 'en' {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }
}

function normalizedValue(value: string): string | undefined {
  const trimmed = value.trim();
  return trimmed ? trimmed : undefined;
}

function singleValueArray(value: string): string[] | undefined {
  const normalized = normalizedValue(value);
  return normalized === undefined ? undefined : [normalized];
}
