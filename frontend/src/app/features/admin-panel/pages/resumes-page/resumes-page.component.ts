import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Router, RouterLink } from '@angular/router';
import { ApiError } from '../../../../core/models/api-error.model';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { formatLocalizedDate } from '../../../../shared/utils/localized-date';
import {
  Resume,
  ResumeLanguage,
  ResumePayload,
  Resumes,
} from '../../models/resume-workspace.model';
import { ResumeWorkspaceService } from '../../services/resume-workspace.service';
import {
  AdminUnsavedChangesService,
  AdminUnsavedChangesSource,
} from '../../services/admin-unsaved-changes.service';
import {
  ADMIN_VALIDATION_LIMITS,
  controlInvalid,
  trimRequired,
  validationMessage,
} from '../../utils/admin-validation';

const PAGE_SIZE = 20;
type RequiredCreateField = 'title' | 'language' | 'fullName' | 'role' | 'summary';

interface ResumeLanguageOption {
  value: ResumeLanguage;
  labelKey: string;
}

const RESUME_LANGUAGE_OPTIONS: readonly ResumeLanguageOption[] = [
  { value: 'ru', labelKey: 'adminResumeWorkspace.languageRu' },
  { value: 'en', labelKey: 'adminResumeWorkspace.languageEn' },
];

@Component({
  selector: 'app-admin-resumes-page',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    TranslatePipe,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './resumes-page.component.html',
  styleUrl: './resumes-page.component.scss',
})
export class AdminResumesPageComponent implements OnInit {
  private readonly resumeWorkspace = inject(ResumeWorkspaceService);
  private readonly notifications = inject(NotificationService);
  private readonly i18n = inject(I18nService);
  private readonly router = inject(Router);
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);
  private readonly unsavedChangesScope = inject(AdminUnsavedChangesService).createScope(
    this.destroyRef,
  );
  private readonly createFormUnsavedSource: AdminUnsavedChangesSource;

  readonly page = signal(1);
  readonly resumes = signal<Resumes | null>(null);
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly createDialogOpen = signal(false);
  readonly createSubmitting = signal(false);
  readonly createFormSubmitted = signal(false);
  readonly createError = signal<ApiError | null>(null);
  readonly createFormSnapshot = signal({
    title: '',
    language: '',
    fullName: '',
    role: '',
    summary: '',
  });
  readonly languageOptions = RESUME_LANGUAGE_OPTIONS;
  readonly validationLimits = ADMIN_VALIDATION_LIMITS;

  readonly createForm = this.formBuilder.group({
    title: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)]],
    language: ['', trimRequired],
    fullName: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)]],
    role: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)]],
    summary: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.resumeLongText)]],
  });

  constructor() {
    this.createFormSnapshot.set(this.createForm.getRawValue());
    this.createFormUnsavedSource = this.unsavedChangesScope.registerSource(
      this.createFormSnapshot,
      this.createDialogOpen,
    );
    this.createForm.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => {
      this.createFormSnapshot.set(this.createForm.getRawValue());
    });
  }

  ngOnInit(): void {
    this.loadResumes();
  }

  loadResumes(): void {
    this.loading.set(true);
    this.error.set(null);
    this.resumeWorkspace
      .listResumes({ page: this.page(), pageSize: PAGE_SIZE })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (resumes) => {
          this.resumes.set(resumes);
          this.loading.set(false);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
          this.notifications.error(this.i18n.translate('adminResumeWorkspace.loadError'));
        },
      });
  }

  previousPage(): void {
    if (this.page() <= 1) return;
    this.page.update((page) => page - 1);
    this.loadResumes();
  }

  nextPage(): void {
    if (this.page() >= (this.resumes()?.totalPages ?? 1)) return;
    this.page.update((page) => page + 1);
    this.loadResumes();
  }

  openCreateDialog(): void {
    this.createForm.reset({
      title: '',
      language: '',
      fullName: '',
      role: '',
      summary: '',
    });
    this.createError.set(null);
    this.createSubmitting.set(false);
    this.createFormSubmitted.set(false);
    this.createFormUnsavedSource.commit();
    this.createDialogOpen.set(true);
  }

  closeCreateDialog(): void {
    if (this.createSubmitting()) return;
    if (!this.unsavedChangesScope.confirmDiscard()) return;
    this.createDialogOpen.set(false);
    this.createError.set(null);
    this.createFormSubmitted.set(false);
  }

  createResume(): void {
    this.createFormSubmitted.set(true);
    if (this.createForm.invalid) {
      this.createForm.markAllAsTouched();
      return;
    }
    this.createSubmitting.set(true);
    this.createError.set(null);
    this.resumeWorkspace
      .createResume(this.buildCreatePayload())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (resume) => {
          this.createSubmitting.set(false);
          this.createFormUnsavedSource.commit();
          this.createDialogOpen.set(false);
          this.notifications.success(this.i18n.translate('adminResumeWorkspace.saved'));
          this.router.navigateByUrl(`/admin-panel/workspace/resumes/${resume.id}`);
        },
        error: (err: ApiError) => {
          this.createError.set(err);
          this.createSubmitting.set(false);
          this.notifications.error(this.i18n.translate('adminResumeWorkspace.saveError'));
        },
      });
  }

  completedSections(resume: Resume): number {
    return [
      resume.title.trim(),
      resume.content.profile.fullName.trim() || resume.content.profile.role.trim(),
      resume.content.summary.text.trim(),
      resume.content.skills.length > 0,
      resume.content.experience.length > 0,
    ].filter(Boolean).length;
  }

  languageLabelKey(language: ResumeLanguage): string {
    return language === 'ru'
      ? 'adminResumeWorkspace.languageRu'
      : 'adminResumeWorkspace.languageEn';
  }

  formatDate(value: string): string {
    return formatLocalizedDate(value, this.i18n.dateLocale(), 'date');
  }

  createFieldInvalid(field: RequiredCreateField): boolean {
    return controlInvalid(this.createForm.controls[field], this.createFormSubmitted());
  }

  createFieldMessage(field: RequiredCreateField): string | null {
    return validationMessage(this.createForm.controls[field], this.i18n);
  }

  private buildCreatePayload(): ResumePayload {
    const value = this.createForm.getRawValue();
    return {
      title: value.title.trim(),
      language: toResumeLanguage(value.language),
      content: {
        profile: {
          fullName: value.fullName.trim(),
          role: value.role.trim(),
          location: '',
          email: '',
          phone: '',
          websiteUrl: '',
          linkedinUrl: '',
          githubUrl: '',
          telegram: '',
        },
        summary: {
          text: value.summary.trim(),
        },
        skills: [],
        experience: [],
        education: [],
        languages: [],
        certifications: [],
        additionalSections: [],
      },
    };
  }
}

function toResumeLanguage(value: string): ResumeLanguage {
  if (value === 'ru' || value === 'en') return value;
  throw new Error(`Unsupported resume language: ${value}`);
}
