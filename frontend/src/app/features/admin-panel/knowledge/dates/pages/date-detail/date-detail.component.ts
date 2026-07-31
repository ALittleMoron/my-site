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
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { I18nService } from '../../../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { ApiError } from '../../../../../../core/models/api-error.model';
import { NotificationService } from '../../../../../../core/notifications/notification.service';
import { ErrorMessageComponent } from '../../../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../../../shared/ui/loading-spinner/loading-spinner.component';
import {
  SiteSelectComponent,
  SiteSelectOption,
} from '../../../../../../shared/ui/site-select/site-select.component';
import {
  AdminAction,
  AdminActionsDropdownComponent,
} from '../../../../components/admin-actions-dropdown/admin-actions-dropdown.component';
import {
  AdminUnsavedChangesService,
  AdminUnsavedChangesSource,
} from '../../../../services/admin-unsaved-changes.service';
import {
  ADMIN_VALIDATION_LIMITS,
  controlInvalid,
  trimRequired,
  validationMessage,
} from '../../../../utils/admin-validation';
import { KnowledgeFile, KnowledgeTag, PersonSummary } from '../../../people/models/people.model';
import { PeopleService } from '../../../people/services/people.service';
import { annualDateValidator } from '../../../shared/annual-date';
import {
  KnowledgeDateDetail,
  KnowledgeDateUpdatePayload,
  RelatedPerson,
} from '../../models/dates.model';
import { KnowledgeDatesService } from '../../services/dates.service';

interface DateFormValue {
  displayName: string;
  date: {
    day: string;
    month: string;
    year: string;
  };
  description: string;
}

@Component({
  selector: 'app-date-detail',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    TranslatePipe,
    MarkdownEditorComponent,
    ErrorMessageComponent,
    LoadingSpinnerComponent,
    SiteSelectComponent,
    AdminActionsDropdownComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './date-detail.component.html',
  styleUrl: './date-detail.component.scss',
})
export class DateDetailComponent implements OnInit {
  private readonly datesService = inject(KnowledgeDatesService);
  private readonly peopleService = inject(PeopleService);
  private readonly notifications = inject(NotificationService);
  private readonly i18n = inject(I18nService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly document = inject(DOCUMENT);
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);
  private readonly unsavedScope = inject(AdminUnsavedChangesService).createScope(this.destroyRef);
  private readonly mainUnsavedSource: AdminUnsavedChangesSource;
  private dateId = '';
  private peopleSearchGeneration = 0;

  readonly loading = signal(true);
  readonly error = signal<ApiError | null>(null);
  readonly date = signal<KnowledgeDateDetail | null>(null);
  readonly saving = signal(false);
  readonly deleting = signal(false);
  readonly submitted = signal(false);
  readonly tags = signal<readonly KnowledgeTag[]>([]);
  readonly selectedTagIds = signal<readonly string[]>([]);
  readonly selectedPeople = signal<readonly RelatedPerson[]>([]);
  readonly personCandidates = signal<readonly PersonSummary[]>([]);
  readonly attachmentUploading = signal(false);
  readonly attachmentError = signal<string | null>(null);
  readonly formSnapshot = signal<DateFormValue>(emptyDateFormValue());

  readonly dateForm = this.formBuilder.group({
    displayName: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)]],
    date: this.formBuilder.group(
      {
        day: [''],
        month: [''],
        year: [''],
      },
      { validators: annualDateValidator },
    ),
    description: ['', Validators.maxLength(100000)],
  });
  readonly mainSnapshot = computed(() => ({
    form: this.formSnapshot(),
    tagIds: this.selectedTagIds(),
    personIds: this.selectedPeople().map((person) => person.id),
  }));
  private readonly mainSourceActive = computed(() => this.date() !== null && !this.loading());
  readonly dayOptions: readonly SiteSelectOption[] = Array.from({ length: 31 }, (_, index) => ({
    value: String(index + 1),
    label: String(index + 1),
  }));
  readonly monthOptions = computed<readonly SiteSelectOption[]>(() => {
    const locale = this.i18n.dateLocale();
    return Array.from({ length: 12 }, (_, index) => ({
      value: String(index + 1),
      label: new Intl.DateTimeFormat(locale, { month: 'long', timeZone: 'UTC' }).format(
        new Date(Date.UTC(2000, index, 1)),
      ),
    }));
  });
  readonly availablePeople = computed(() => {
    const selectedIds = new Set(this.selectedPeople().map((person) => person.id));
    return this.personCandidates().filter((person) => !selectedIds.has(person.id));
  });
  readonly editorLanguage = computed(() => {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('UI language must be initialized before Dates editor');
    }
    return language;
  });
  readonly validationLimits = ADMIN_VALIDATION_LIMITS;

  constructor() {
    this.mainUnsavedSource = this.unsavedScope.registerSource(
      this.mainSnapshot,
      this.mainSourceActive,
    );
    this.dateForm.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => {
      this.formSnapshot.set(this.dateForm.getRawValue());
    });
  }

  ngOnInit(): void {
    this.dateId = this.route.snapshot.paramMap.get('id') ?? '';
    this.loadDate();
    this.loadTags();
    this.searchPeople('');
  }

  loadDate(): void {
    this.loading.set(true);
    this.error.set(null);
    this.datesService
      .getDate(this.dateId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (value) => {
          this.date.set(value);
          this.patchDate(value);
          this.loading.set(false);
        },
        error: (error: ApiError) => {
          this.error.set(error);
          this.loading.set(false);
          this.notifications.error(this.i18n.translate('knowledgeDates.detailLoadError'));
        },
      });
  }

  loadTags(): void {
    this.peopleService
      .listTags('')
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tags) => this.tags.set(tags),
        error: () => this.notifications.error(this.i18n.translate('knowledgeDates.tagsLoadError')),
      });
  }

  searchPeople(query: string): void {
    const generation = ++this.peopleSearchGeneration;
    this.peopleService
      .listPeople({
        page: 1,
        pageSize: 100,
        sort: 'nameAsc',
        searchQuery: query,
        tagIds: [],
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (page) => {
          if (generation === this.peopleSearchGeneration) {
            this.personCandidates.set(page.people);
          }
        },
        error: () => {
          if (generation === this.peopleSearchGeneration) {
            this.notifications.error(this.i18n.translate('knowledgeDates.peopleSearchError'));
          }
        },
      });
  }

  saveDate(): void {
    this.submitted.set(true);
    this.dateForm.markAllAsTouched();
    if (this.dateForm.invalid) {
      this.notifications.error(this.i18n.translate('knowledgeDates.validationError'));
      return;
    }
    this.saving.set(true);
    this.datesService
      .updateDate(this.dateId, this.buildPayload())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (value) => {
          this.date.set(value);
          this.patchDate(value);
          this.saving.set(false);
          this.submitted.set(false);
          this.notifications.success(this.i18n.translate('knowledgeDates.saveSuccess'));
        },
        error: () => {
          this.saving.set(false);
          this.notifications.error(this.i18n.translate('knowledgeDates.saveError'));
        },
      });
  }

  deleteDate(): void {
    const value = this.date();
    const browserWindow = this.document.defaultView;
    if (
      value === null ||
      browserWindow === null ||
      !browserWindow.confirm(
        this.i18n.translate('knowledgeDates.deleteConfirm', { name: value.displayName }),
      )
    ) {
      return;
    }
    this.deleting.set(true);
    this.datesService
      .deleteDate(value.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.mainUnsavedSource.commit();
          this.notifications.success(this.i18n.translate('knowledgeDates.deleteSuccess'));
          this.back();
        },
        error: () => {
          this.deleting.set(false);
          this.notifications.error(this.i18n.translate('knowledgeDates.deleteError'));
        },
      });
  }

  detailActions(): AdminAction[] {
    return [
      {
        id: 'delete',
        label: this.i18n.translate('shared.delete'),
        destructive: true,
        disabled: this.saving() || this.deleting() || this.loading(),
      },
    ];
  }

  handleDetailAction(actionId: string): void {
    if (actionId === 'delete') {
      this.deleteDate();
      return;
    }
    throw new Error(`Unsupported Dates detail action: ${actionId}`);
  }

  back(): void {
    void this.router.navigate(['/admin-panel/knowledge/dates'], {
      queryParamsHandling: 'preserve',
    });
  }

  setDescription(value: string): void {
    this.dateForm.controls.description.setValue(value);
    this.dateForm.controls.description.markAsDirty();
  }

  toggleTag(tagId: string): void {
    this.selectedTagIds.update((ids) =>
      ids.includes(tagId) ? ids.filter((id) => id !== tagId) : [...ids, tagId],
    );
  }

  addPerson(person: PersonSummary): void {
    if (this.selectedPeople().some((value) => value.id === person.id)) {
      return;
    }
    this.selectedPeople.update((values) => [
      ...values,
      { id: person.id, displayName: person.displayName },
    ]);
  }

  removePerson(personId: string): void {
    this.selectedPeople.update((values) => values.filter((value) => value.id !== personId));
  }

  uploadAttachment(event: Event): void {
    const input = event.currentTarget;
    if (!(input instanceof HTMLInputElement) || input.files?.[0] === undefined) {
      return;
    }
    const file = input.files[0];
    this.attachmentUploading.set(true);
    this.attachmentError.set(null);
    this.datesService
      .uploadAttachment(this.dateId, file, file.name)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (attachment) => {
          input.value = '';
          this.attachmentUploading.set(false);
          this.date.update((value) =>
            value === null ? null : { ...value, attachments: [...value.attachments, attachment] },
          );
          this.notifications.success(this.i18n.translate('knowledgeDates.attachmentSaveSuccess'));
        },
        error: () => {
          this.attachmentUploading.set(false);
          this.attachmentError.set(this.i18n.translate('knowledgeDates.attachmentSaveError'));
          this.notifications.error(this.i18n.translate('knowledgeDates.attachmentSaveError'));
        },
      });
  }

  renameAttachment(attachment: KnowledgeFile): void {
    const name = this.document.defaultView?.prompt(
      this.i18n.translate('knowledgeDates.attachmentRenamePrompt'),
      attachment.name,
    );
    if (name === undefined || name === null || name.trim() === '') {
      return;
    }
    this.datesService
      .renameAttachment(this.dateId, attachment.id, name.trim())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (updated) => {
          this.date.update((value) =>
            value === null
              ? null
              : {
                  ...value,
                  attachments: value.attachments.map((file) =>
                    file.id === updated.id ? updated : file,
                  ),
                },
          );
          this.notifications.success(this.i18n.translate('knowledgeDates.attachmentRenameSuccess'));
        },
        error: () =>
          this.notifications.error(this.i18n.translate('knowledgeDates.attachmentRenameError')),
      });
  }

  deleteAttachment(attachment: KnowledgeFile): void {
    const browserWindow = this.document.defaultView;
    if (
      browserWindow === null ||
      !browserWindow.confirm(
        this.i18n.translate('knowledgeDates.attachmentDeleteConfirm', {
          name: attachment.name,
        }),
      )
    ) {
      return;
    }
    this.datesService
      .deleteAttachment(this.dateId, attachment.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.date.update((value) =>
            value === null
              ? null
              : {
                  ...value,
                  attachments: value.attachments.filter((file) => file.id !== attachment.id),
                },
          );
          this.notifications.success(this.i18n.translate('knowledgeDates.attachmentDeleteSuccess'));
        },
        error: () =>
          this.notifications.error(this.i18n.translate('knowledgeDates.attachmentDeleteError')),
      });
  }

  downloadAttachment(attachment: KnowledgeFile): void {
    const browserWindow = this.document.defaultView;
    if (browserWindow === null) {
      this.notifications.error(this.i18n.translate('knowledgeDates.attachmentDownloadError'));
      return;
    }
    this.datesService
      .getFileContent(attachment.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (blob) => {
          const url = browserWindow.URL.createObjectURL(blob);
          try {
            const anchor = this.document.createElement('a');
            anchor.href = url;
            anchor.download = attachment.originalName;
            anchor.click();
          } finally {
            browserWindow.URL.revokeObjectURL(url);
          }
        },
        error: () =>
          this.notifications.error(this.i18n.translate('knowledgeDates.attachmentDownloadError')),
      });
  }

  nameInvalid(): boolean {
    return controlInvalid(this.dateForm.controls.displayName, this.submitted());
  }

  nameMessage(): string | null {
    return validationMessage(this.dateForm.controls.displayName, this.i18n);
  }

  annualDateInvalid(): boolean {
    return this.dateForm.controls.date.invalid && this.submitted();
  }

  fileSize(sizeBytes: number): string {
    return new Intl.NumberFormat(this.i18n.dateLocale(), {
      style: 'unit',
      unit: 'megabyte',
      unitDisplay: 'short',
      maximumFractionDigits: 2,
    }).format(sizeBytes / (1024 * 1024));
  }

  private patchDate(value: KnowledgeDateDetail): void {
    this.dateForm.setValue({
      displayName: value.displayName,
      date: {
        day: String(value.date.day),
        month: String(value.date.month),
        year: value.date.year === null ? '' : String(value.date.year),
      },
      description: value.description,
    });
    this.selectedTagIds.set(value.tags.map((tag) => tag.id));
    this.selectedPeople.set(value.relatedPeople.map((person) => ({ ...person })));
    this.formSnapshot.set(this.dateForm.getRawValue());
    this.mainUnsavedSource.commit();
  }

  private buildPayload(): KnowledgeDateUpdatePayload {
    const value = this.dateForm.getRawValue();
    return {
      displayName: value.displayName.trim(),
      date: {
        day: Number(value.date.day),
        month: Number(value.date.month),
        year: value.date.year === '' ? null : Number(value.date.year),
      },
      description: value.description,
      tagIds: this.selectedTagIds(),
      personIds: this.selectedPeople().map((person) => person.id),
    };
  }
}

function emptyDateFormValue(): DateFormValue {
  return {
    displayName: '',
    date: { day: '', month: '', year: '' },
    description: '',
  };
}
