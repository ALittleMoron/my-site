import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { DOCUMENT } from '@angular/common';
import { RouterLink } from '@angular/router';
import {
  AbstractControl,
  NonNullableFormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ApiError } from '../../../../core/models/api-error.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { slugify } from '../../../../shared/utils/slugify';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { MatrixGroupedListComponent } from '../../../../shared/ui/matrix-grouped-list/matrix-grouped-list.component';
import { MatrixSheetTabsComponent } from '../../../../shared/ui/matrix-sheet-tabs/matrix-sheet-tabs.component';
import {
  AdminMatrixGrade,
  AdminMatrixMissingField,
  AdminMatrixPublishStatus,
  AdminMatrixQuestionDetailDto,
  AdminMatrixQuestionPayload,
  AdminMatrixResource,
  AdminMatrixResourceAttachmentPayload,
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
const PUBLISH_STATUSES: readonly AdminMatrixPublishStatus[] = ['Draft', 'Published'];
const SORTS: readonly AdminMatrixWorkspaceSort[] = [
  'newest',
  'oldest',
  'grade',
  'section',
  'subsection',
  'missingFields',
  'dangerousPublished',
];
const PAGE_SIZES: readonly number[] = [20, 50, 100];
const RESOURCE_SEARCH_LIMIT = 10;
const PUBLICATION_FIELDS: readonly AdminMatrixMissingField[] = [
  'slug',
  'sheetKey',
  'grade',
  'questionRu',
  'questionEn',
  'answerRu',
  'answerEn',
  'interviewExpectedAnswerRu',
  'interviewExpectedAnswerEn',
  'sheetRu',
  'sheetEn',
  'sectionRu',
  'sectionEn',
  'subsectionRu',
  'subsectionEn',
];

type WorkspaceTab = 'list' | 'preview';
type RequiredFormField = 'slug' | 'sheetKey' | 'questionRu' | 'questionEn';

interface AdminMatrixAttachedResourceTranslations {
  ru: { name: string; context: string };
  en: { name: string; context: string };
}

interface AdminMatrixResourceDraft {
  id: number;
  name: string;
  url: string;
  context: string;
  isNew: boolean;
  translations: AdminMatrixAttachedResourceTranslations;
}

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
    MatrixGroupedListComponent,
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

  readonly grades = GRADES;
  readonly publishStatuses = PUBLISH_STATUSES;
  readonly sorts = SORTS;
  readonly pageSizes = PAGE_SIZES;

  readonly activeTab = signal<WorkspaceTab>('list');
  readonly workspace = signal<AdminMatrixQuestionWorkspace | null>(null);
  readonly filterOptions = signal<AdminMatrixWorkspaceFilterOptions>({
    sheets: [],
    grades: [],
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

  readonly formMode = signal<'create' | 'edit' | null>(null);
  readonly formLoading = signal(false);
  readonly formSubmitting = signal(false);
  readonly formSubmitted = signal(false);
  readonly formError = signal<ApiError | null>(null);
  readonly editingQuestion = signal<AdminMatrixQuestionDetailDto | null>(null);
  readonly resourceDrafts = signal<AdminMatrixResourceDraft[]>([]);
  readonly resourceSearchResults = signal<AdminMatrixResource[]>([]);
  readonly newResourceNameRu = signal('');
  readonly newResourceNameEn = signal('');
  readonly newResourceUrl = signal('');

  private nextNewResourceId = -1;

  readonly filtersForm = this.formBuilder.group({
    searchQuery: [''],
    sheetKey: [''],
    grade: [''],
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

  readonly questionForm = this.formBuilder.group({
    slug: ['', [trimRequired, Validators.maxLength(255)]],
    sheetKey: ['', [trimRequired, Validators.maxLength(255)]],
    grade: this.formBuilder.control<AdminMatrixGrade | ''>(''),
    publishStatus: this.formBuilder.control<AdminMatrixPublishStatus>('Draft', {
      validators: Validators.required,
    }),
    questionRu: ['', [trimRequired, Validators.maxLength(255)]],
    questionEn: ['', [trimRequired, Validators.maxLength(255)]],
    answerRu: [''],
    answerEn: [''],
    expectedAnswerRu: [''],
    expectedAnswerEn: [''],
    sheetRu: ['', Validators.maxLength(255)],
    sheetEn: ['', Validators.maxLength(255)],
    sectionRu: ['', Validators.maxLength(255)],
    sectionEn: ['', Validators.maxLength(255)],
    subsectionRu: ['', Validators.maxLength(255)],
    subsectionEn: ['', Validators.maxLength(255)],
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
    this.formLoading.set(false);
    this.formSubmitted.set(false);
    this.editingQuestion.set(null);
    this.resetResourceDrafts();
    this.questionForm.reset({
      slug: '',
      sheetKey: '',
      grade: '',
      publishStatus: 'Draft',
      questionRu: '',
      questionEn: '',
      answerRu: '',
      answerEn: '',
      expectedAnswerRu: '',
      expectedAnswerEn: '',
      sheetRu: '',
      sheetEn: '',
      sectionRu: '',
      sectionEn: '',
      subsectionRu: '',
      subsectionEn: '',
    });
  }

  openEdit(item: AdminMatrixWorkspaceItem): void {
    this.formMode.set('edit');
    this.formLoading.set(true);
    this.formError.set(null);
    this.formSubmitted.set(false);
    this.editingQuestion.set(null);
    this.resetResourceDrafts();
    this.workspaceService
      .getQuestion(item.id, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (detail) => {
          this.editingQuestion.set(detail);
          this.populateQuestionForm(detail);
          this.formLoading.set(false);
        },
        error: (err: ApiError) => {
          this.formError.set(err);
          this.formLoading.set(false);
        },
      });
  }

  closeForm(): void {
    if (this.formSubmitting()) return;
    this.formMode.set(null);
    this.formError.set(null);
    this.formSubmitted.set(false);
    this.editingQuestion.set(null);
    this.resetResourceDrafts();
  }

  saveQuestion(): void {
    this.formSubmitted.set(true);
    if (this.questionForm.invalid) {
      this.questionForm.markAllAsTouched();
      return;
    }
    const payload = this.buildQuestionPayload();
    const missingFields = this.missingPayloadFields(payload);
    if (payload.publishStatus === 'Published' && missingFields.length > 0) {
      this.notifications.error(
        this.i18n.translate('adminMatrixWorkspace.publishMissingFields', {
          fields: this.missingFieldsText(missingFields),
        }),
      );
      return;
    }
    const editingQuestion = this.editingQuestion();
    const request =
      this.formMode() === 'edit' && editingQuestion !== null
        ? this.workspaceService.updateQuestion(editingQuestion.id, payload, this.currentLanguage())
        : this.workspaceService.createQuestion(payload, this.currentLanguage());
    this.formSubmitting.set(true);
    this.formError.set(null);
    request.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
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

  gradeLabel(grade: AdminMatrixGrade | null): string {
    return grade === null
      ? this.i18n.translate('shared.notSet')
      : this.i18n.translate(this.i18n.enumGradeKey(grade));
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

  fieldInvalid(field: RequiredFormField): boolean {
    const control = this.questionForm.controls[field];
    return control.invalid && (this.formSubmitted() || control.touched);
  }

  generateSlug(): void {
    const source = this.questionForm.controls.questionEn.value.trim();
    if (!source) return;
    this.questionForm.controls.slug.setValue(slugify(source));
    this.questionForm.controls.slug.markAsDirty();
    this.questionForm.controls.slug.markAsTouched();
  }

  canGenerateSlug(): boolean {
    return this.questionForm.controls.questionEn.value.trim() !== '';
  }

  searchResources(value: string): void {
    const searchName = value.trim();
    if (searchName.length < 2) {
      this.resourceSearchResults.set([]);
      return;
    }
    this.workspaceService
      .searchResources(searchName, RESOURCE_SEARCH_LIMIT, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (resources) => this.resourceSearchResults.set(resources),
        error: () => {
          this.resourceSearchResults.set([]);
          this.notifications.error(this.i18n.translate('matrix.notify.resourcesError'));
        },
      });
  }

  attachResource(resource: AdminMatrixResource): void {
    if (this.resourceDrafts().some((draft) => !draft.isNew && draft.id === resource.id)) return;
    this.resourceDrafts.update((drafts) => [
      ...drafts,
      {
        ...resource,
        context: '',
        translations: {
          ru: { name: resource.translations.ru.name, context: '' },
          en: { name: resource.translations.en.name, context: '' },
        },
        isNew: false,
      },
    ]);
  }

  addNewResource(): void {
    const nameRu = this.newResourceNameRu().trim();
    const nameEn = this.newResourceNameEn().trim();
    const url = this.newResourceUrl().trim();
    if (!nameRu || !nameEn || !url) return;
    this.resourceDrafts.update((drafts) => [
      ...drafts,
      {
        id: this.nextNewResourceId--,
        name: this.currentLanguage() === 'ru' ? nameRu : nameEn,
        url,
        context: '',
        translations: {
          ru: { name: nameRu, context: '' },
          en: { name: nameEn, context: '' },
        },
        isNew: true,
      },
    ]);
    this.newResourceNameRu.set('');
    this.newResourceNameEn.set('');
    this.newResourceUrl.set('');
  }

  updateResourceContext(index: number, language: 'ru' | 'en', context: string): void {
    this.resourceDrafts.update((drafts) =>
      drafts.map((draft, currentIndex) =>
        currentIndex === index
          ? {
              ...draft,
              context: language === this.currentLanguage() ? context : draft.context,
              translations: {
                ...draft.translations,
                [language]: { ...draft.translations[language], context },
              },
            }
          : draft,
      ),
    );
  }

  detachResource(index: number): void {
    this.resourceDrafts.update((drafts) =>
      drafts.filter((_, currentIndex) => currentIndex !== index),
    );
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
      sections: singleValueArray(raw.section),
      subsections: singleValueArray(raw.subsection),
      publishStatuses: singleValueArray(raw.publishStatus) as AdminMatrixPublishStatus[],
      publishedFrom: normalizedValue(raw.publishedFrom),
      publishedTo: normalizedValue(raw.publishedTo),
      hasMissingFields: raw.hasMissingFields === '' ? undefined : raw.hasMissingFields === 'true',
    };
  }

  private populateQuestionForm(detail: AdminMatrixQuestionDetailDto): void {
    this.questionForm.reset({
      slug: detail.slug,
      sheetKey: detail.sheetKey,
      grade: detail.grade ?? '',
      publishStatus: detail.publishStatus,
      questionRu: detail.translations.ru.question,
      questionEn: detail.translations.en.question,
      answerRu: detail.translations.ru.answer,
      answerEn: detail.translations.en.answer,
      expectedAnswerRu: detail.translations.ru.interviewExpectedAnswer,
      expectedAnswerEn: detail.translations.en.interviewExpectedAnswer,
      sheetRu: detail.translations.ru.sheet,
      sheetEn: detail.translations.en.sheet,
      sectionRu: detail.translations.ru.section,
      sectionEn: detail.translations.en.section,
      subsectionRu: detail.translations.ru.subsection,
      subsectionEn: detail.translations.en.subsection,
    });
    this.resourceDrafts.set(detail.resources.map(toResourceDraft));
  }

  private buildQuestionPayload(): AdminMatrixQuestionPayload {
    const raw = this.questionForm.getRawValue();
    return {
      slug: raw.slug.trim(),
      sheetKey: raw.sheetKey.trim(),
      grade: raw.grade === '' ? null : raw.grade,
      publishStatus: raw.publishStatus,
      translations: {
        ru: {
          question: raw.questionRu.trim(),
          answer: raw.answerRu,
          interviewExpectedAnswer: raw.expectedAnswerRu,
          sheet: raw.sheetRu.trim(),
          section: raw.sectionRu.trim(),
          subsection: raw.subsectionRu.trim(),
        },
        en: {
          question: raw.questionEn.trim(),
          answer: raw.answerEn,
          interviewExpectedAnswer: raw.expectedAnswerEn,
          sheet: raw.sheetEn.trim(),
          section: raw.sectionEn.trim(),
          subsection: raw.subsectionEn.trim(),
        },
      },
      resources: this.resourceDrafts().map(toResourceAttachmentPayload),
    };
  }

  private missingPayloadFields(payload: AdminMatrixQuestionPayload): AdminMatrixMissingField[] {
    return PUBLICATION_FIELDS.filter((field) => isPayloadFieldMissing(payload, field));
  }

  private resetResourceDrafts(): void {
    this.resourceDrafts.set([]);
    this.resourceSearchResults.set([]);
    this.newResourceNameRu.set('');
    this.newResourceNameEn.set('');
    this.newResourceUrl.set('');
    this.nextNewResourceId = -1;
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

  private currentLanguage(): 'ru' | 'en' {
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

function trimRequired(control: AbstractControl<string>): ValidationErrors | null {
  return control.value.trim() === '' ? { required: true } : null;
}

function toResourceDraft(
  resource: AdminMatrixQuestionDetailDto['resources'][number],
): AdminMatrixResourceDraft {
  return {
    ...resource,
    translations: resource.translations,
    isNew: false,
  };
}

function toResourceAttachmentPayload(
  resource: AdminMatrixResourceDraft,
): AdminMatrixResourceAttachmentPayload {
  if (resource.isNew) {
    return {
      resource: {
        url: resource.url,
        translations: {
          ru: { name: resource.translations.ru.name },
          en: { name: resource.translations.en.name },
        },
      },
      translations: {
        ru: { context: resource.translations.ru.context },
        en: { context: resource.translations.en.context },
      },
    };
  }
  return {
    resourceId: resource.id,
    translations: {
      ru: { context: resource.translations.ru.context },
      en: { context: resource.translations.en.context },
    },
  };
}

function isPayloadFieldMissing(
  payload: AdminMatrixQuestionPayload,
  field: AdminMatrixMissingField,
): boolean {
  switch (field) {
    case 'slug':
      return payload.slug.trim() === '';
    case 'sheetKey':
      return payload.sheetKey.trim() === '';
    case 'grade':
      return payload.grade === null;
    case 'questionRu':
      return payload.translations.ru.question.trim() === '';
    case 'questionEn':
      return payload.translations.en.question.trim() === '';
    case 'answerRu':
      return payload.translations.ru.answer.trim() === '';
    case 'answerEn':
      return payload.translations.en.answer.trim() === '';
    case 'interviewExpectedAnswerRu':
      return payload.translations.ru.interviewExpectedAnswer.trim() === '';
    case 'interviewExpectedAnswerEn':
      return payload.translations.en.interviewExpectedAnswer.trim() === '';
    case 'sheetRu':
      return payload.translations.ru.sheet.trim() === '';
    case 'sheetEn':
      return payload.translations.en.sheet.trim() === '';
    case 'sectionRu':
      return payload.translations.ru.section.trim() === '';
    case 'sectionEn':
      return payload.translations.en.section.trim() === '';
    case 'subsectionRu':
      return payload.translations.ru.subsection.trim() === '';
    case 'subsectionEn':
      return payload.translations.en.subsection.trim() === '';
  }
}
