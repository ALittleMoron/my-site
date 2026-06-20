import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import {
  AbstractControl,
  NonNullableFormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Router, RouterLink } from '@angular/router';
import { ApiError } from '../../../../core/models/api-error.model';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { Resume, ResumePayload, Resumes } from '../../models/resume-workspace.model';
import { ResumeWorkspaceService } from '../../services/resume-workspace.service';

const PAGE_SIZE = 20;
type RequiredCreateField = 'title' | 'fullName' | 'roleRu' | 'roleEn' | 'summaryRu' | 'summaryEn';

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

  readonly page = signal(1);
  readonly resumes = signal<Resumes | null>(null);
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly createDialogOpen = signal(false);
  readonly createSubmitting = signal(false);
  readonly createFormSubmitted = signal(false);
  readonly createError = signal<ApiError | null>(null);

  readonly createForm = this.formBuilder.group({
    title: ['', [trimRequired, Validators.maxLength(255)]],
    fullName: ['', [trimRequired, Validators.maxLength(255)]],
    roleRu: ['', [trimRequired, Validators.maxLength(255)]],
    roleEn: ['', [trimRequired, Validators.maxLength(255)]],
    summaryRu: ['', trimRequired],
    summaryEn: ['', trimRequired],
  });

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
      fullName: '',
      roleRu: '',
      roleEn: '',
      summaryRu: '',
      summaryEn: '',
    });
    this.createError.set(null);
    this.createSubmitting.set(false);
    this.createFormSubmitted.set(false);
    this.createDialogOpen.set(true);
  }

  closeCreateDialog(): void {
    if (this.createSubmitting()) return;
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
      resume.content.profile.fullName?.trim() || resume.content.profile.roleRu?.trim(),
      resume.content.summary.textRu?.trim() || resume.content.summary.textEn?.trim(),
      resume.content.skills.length > 0,
      resume.content.experience.length > 0,
    ].filter(Boolean).length;
  }

  formatDate(value: string): string {
    return value.slice(0, 10);
  }

  createFieldInvalid(field: RequiredCreateField): boolean {
    const control = this.createForm.controls[field];
    return control.invalid && (this.createFormSubmitted() || control.touched);
  }

  private buildCreatePayload(): ResumePayload {
    const value = this.createForm.getRawValue();
    return {
      title: value.title.trim(),
      content: {
        profile: {
          fullName: value.fullName.trim(),
          roleRu: value.roleRu.trim(),
          roleEn: value.roleEn.trim(),
          locationRu: null,
          locationEn: null,
          email: null,
          phone: null,
          websiteUrl: null,
          linkedinUrl: null,
          githubUrl: null,
          telegram: null,
        },
        summary: {
          textRu: value.summaryRu.trim(),
          textEn: value.summaryEn.trim(),
        },
        skills: [],
        experience: [],
        projects: [],
        education: [],
        languages: [],
        certifications: [],
        additionalSections: [],
      },
    };
  }
}

function trimRequired(control: AbstractControl<string>): ValidationErrors | null {
  return control.value.trim() === '' ? { required: true } : null;
}
