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
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  AbstractControl,
  FormArray,
  FormControl,
  FormGroup,
  NonNullableFormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { EMPTY, catchError } from 'rxjs';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { ApiError } from '../../../../core/models/api-error.model';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LocalizedDatePickerComponent } from '../../../../shared/ui/localized-date-picker/localized-date-picker.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { AdminControlValidationStateDirective } from '../../directives/admin-control-validation-state.directive';
import {
  Resume,
  ResumeAdditionalSection,
  ResumeAdditionalSectionItem,
  ResumeCertificationItem,
  ResumeContent,
  ResumeCurrentStatus,
  ResumeEducationItem,
  ResumeExportFormat,
  ResumeExperienceItem,
  ResumeLanguage,
  ResumeLanguageItem,
  ResumePayload,
  ResumeProfile,
  ResumeProjectItem,
  ResumeSkillGroup,
  ResumeSummary,
} from '../../models/resume-workspace.model';
import { ResumeWorkspaceService } from '../../services/resume-workspace.service';
import {
  ADMIN_VALIDATION_LIMITS,
  controlInvalid,
  emailValidator,
  httpUrlValidator,
  trimRequired,
  validationMessage,
} from '../../utils/admin-validation';

type ResumeEditorTab =
  | 'profile'
  | 'summary'
  | 'skills'
  | 'experience'
  | 'education'
  | 'languages'
  | 'certifications'
  | 'additional';
type ResumeEditorMode = 'edit' | 'preview';
type ResumeExportFormatSelection = ResumeExportFormat | '';
type TextControl = FormControl<string>;
type NullableTextControl = FormControl<string | null>;
type CurrentStatusControl = FormControl<ResumeCurrentStatus>;
type ResumeLanguageControl = FormControl<ResumeLanguage | ''>;

interface ResumeEditorTabDefinition {
  key: ResumeEditorTab;
  labelKey: string;
}

interface ResumeCurrentStatusOption {
  value: ResumeCurrentStatus;
  labelKey: string;
}

interface ResumeLanguageOption {
  value: ResumeLanguage;
  labelKey: string;
}

interface ResumeExportFormatOption {
  value: ResumeExportFormat;
  labelKey: string;
}

interface ResumeValidationIssue {
  tab: ResumeEditorTab | null;
  message: string;
}

interface ResumeProfileForm {
  fullName: TextControl;
  role: TextControl;
  location: TextControl;
  email: TextControl;
  phone: TextControl;
  websiteUrl: TextControl;
  linkedinUrl: TextControl;
  githubUrl: TextControl;
  telegram: TextControl;
}

interface ResumeSummaryForm {
  text: TextControl;
}

interface ResumeSkillGroupForm {
  category: TextControl;
  items: FormArray<TextControl>;
}

interface ResumeExperienceItemForm {
  company: TextControl;
  position: TextControl;
  location: TextControl;
  startDate: NullableTextControl;
  endDate: NullableTextControl;
  currentStatus: CurrentStatusControl;
  summary: TextControl;
  highlights: FormArray<TextControl>;
  technologies: FormArray<TextControl>;
  projects: FormArray<FormGroup<ResumeProjectItemForm>>;
}

interface ResumeProjectItemForm {
  name: TextControl;
  role: TextControl;
  description: TextControl;
  highlights: FormArray<TextControl>;
  technologies: FormArray<TextControl>;
  url: TextControl;
}

interface ResumeEducationItemForm {
  institution: TextControl;
  degree: TextControl;
  field: TextControl;
  location: TextControl;
  startDate: NullableTextControl;
  endDate: NullableTextControl;
  description: TextControl;
}

interface ResumeLanguageItemForm {
  name: TextControl;
  proficiency: TextControl;
}

interface ResumeCertificationItemForm {
  name: TextControl;
  issuer: TextControl;
  issuedOn: NullableTextControl;
  expiresOn: NullableTextControl;
  credentialUrl: TextControl;
}

interface ResumeAdditionalSectionItemForm {
  title: TextControl;
  description: TextControl;
  url: TextControl;
}

interface ResumeAdditionalSectionForm {
  title: TextControl;
  items: FormArray<FormGroup<ResumeAdditionalSectionItemForm>>;
}

interface ResumeEditorForm {
  title: TextControl;
  language: ResumeLanguageControl;
  profile: FormGroup<ResumeProfileForm>;
  summary: FormGroup<ResumeSummaryForm>;
  skills: FormArray<FormGroup<ResumeSkillGroupForm>>;
  experience: FormArray<FormGroup<ResumeExperienceItemForm>>;
  education: FormArray<FormGroup<ResumeEducationItemForm>>;
  languages: FormArray<FormGroup<ResumeLanguageItemForm>>;
  certifications: FormArray<FormGroup<ResumeCertificationItemForm>>;
  additionalSections: FormArray<FormGroup<ResumeAdditionalSectionForm>>;
}

const RESUME_EDITOR_TABS: readonly ResumeEditorTabDefinition[] = [
  { key: 'profile', labelKey: 'adminResumeWorkspace.tabs.profile' },
  { key: 'summary', labelKey: 'adminResumeWorkspace.tabs.summary' },
  { key: 'skills', labelKey: 'adminResumeWorkspace.tabs.skills' },
  { key: 'experience', labelKey: 'adminResumeWorkspace.tabs.experience' },
  { key: 'education', labelKey: 'adminResumeWorkspace.tabs.education' },
  { key: 'languages', labelKey: 'adminResumeWorkspace.tabs.languages' },
  { key: 'certifications', labelKey: 'adminResumeWorkspace.tabs.certifications' },
  { key: 'additional', labelKey: 'adminResumeWorkspace.tabs.additional' },
];

const RESUME_CURRENT_STATUS_OPTIONS: readonly ResumeCurrentStatusOption[] = [
  { value: 'notSet', labelKey: 'adminResumeWorkspace.currentStatus.notSet' },
  { value: 'current', labelKey: 'adminResumeWorkspace.currentStatus.current' },
  { value: 'notCurrent', labelKey: 'adminResumeWorkspace.currentStatus.notCurrent' },
];

const RESUME_LANGUAGE_OPTIONS: readonly ResumeLanguageOption[] = [
  { value: 'ru', labelKey: 'adminResumeWorkspace.languageRu' },
  { value: 'en', labelKey: 'adminResumeWorkspace.languageEn' },
];

const RESUME_EXPORT_FORMAT_OPTIONS: readonly ResumeExportFormatOption[] = [
  { value: 'pdf', labelKey: 'adminResumeWorkspace.exportFormatPdf' },
  { value: 'docx', labelKey: 'adminResumeWorkspace.exportFormatDocx' },
];

const INLINE_LIST_INPUT_MIN_TEXT_WIDTH_CH = 5;
const INLINE_LIST_INPUT_MAX_TEXT_WIDTH_CH = 32;
const INLINE_LIST_INPUT_EXTRA_TEXT_WIDTH_CH = 1;
const INLINE_LIST_INPUT_ACTION_WIDTH_REM = 3;

@Component({
  selector: 'app-admin-resume-detail-page',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    TranslatePipe,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    LocalizedDatePickerComponent,
    AdminControlValidationStateDirective,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './resume-detail-page.component.html',
  styleUrl: './resume-detail-page.component.scss',
})
export class AdminResumeDetailPageComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly resumeWorkspace = inject(ResumeWorkspaceService);
  private readonly notifications = inject(NotificationService);
  private readonly i18n = inject(I18nService);
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);
  private readonly document = inject(DOCUMENT);
  private readonly resumeId = this.resolveResumeId();

  readonly tabs = RESUME_EDITOR_TABS;
  readonly currentStatusOptions = RESUME_CURRENT_STATUS_OPTIONS;
  readonly languageOptions = RESUME_LANGUAGE_OPTIONS;
  readonly exportFormats = RESUME_EXPORT_FORMAT_OPTIONS;
  readonly activeTab = signal<ResumeEditorTab>('profile');
  readonly mode = signal<ResumeEditorMode>('edit');
  readonly exportModalOpen = signal(false);
  readonly selectedExportFormat = signal<ResumeExportFormatSelection>('');
  readonly previewLanguage = computed<ResumeLanguage>(() =>
    toResumeLanguage(this.resumeForm.controls.language.getRawValue()),
  );
  readonly dateLocale = computed(() => this.i18n.dateLocale());
  readonly datePlaceholder = computed(() => {
    this.i18n.language();
    return this.i18n.translate('shared.datePicker.placeholder');
  });
  readonly openCalendarLabel = computed(() => {
    this.i18n.language();
    return this.i18n.translate('shared.datePicker.open');
  });
  readonly previousMonthLabel = computed(() => {
    this.i18n.language();
    return this.i18n.translate('shared.datePicker.previousMonth');
  });
  readonly nextMonthLabel = computed(() => {
    this.i18n.language();
    return this.i18n.translate('shared.datePicker.nextMonth');
  });
  readonly openMonthYearPickerLabel = computed(() => {
    this.i18n.language();
    return this.i18n.translate('shared.datePicker.openMonthYearPicker');
  });
  readonly previousYearLabel = computed(() => {
    this.i18n.language();
    return this.i18n.translate('shared.datePicker.previousYear');
  });
  readonly nextYearLabel = computed(() => {
    this.i18n.language();
    return this.i18n.translate('shared.datePicker.nextYear');
  });
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly deleting = signal(false);
  readonly exporting = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly formError = signal<ApiError | null>(null);
  readonly exportError = signal<ApiError | null>(null);
  readonly formVersion = signal(0);
  readonly validationSubmitted = signal(false);
  readonly validationIssues = computed<readonly ResumeValidationIssue[]>(() => {
    this.formVersion();
    this.i18n.language();
    if (!this.validationSubmitted()) return [];
    return this.collectValidationIssues();
  });
  readonly validationLimits = ADMIN_VALIDATION_LIMITS;

  readonly resumeForm = new FormGroup<ResumeEditorForm>({
    title: this.formBuilder.control('', {
      validators: [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)],
    }),
    language: new FormControl<ResumeLanguage | ''>('', {
      nonNullable: true,
      validators: Validators.required,
    }),
    profile: this.createProfileForm(createEmptyResumeProfile()),
    summary: this.createSummaryForm(createEmptyResumeSummary()),
    skills: new FormArray<FormGroup<ResumeSkillGroupForm>>([]),
    experience: new FormArray<FormGroup<ResumeExperienceItemForm>>([]),
    education: new FormArray<FormGroup<ResumeEducationItemForm>>([]),
    languages: new FormArray<FormGroup<ResumeLanguageItemForm>>([]),
    certifications: new FormArray<FormGroup<ResumeCertificationItemForm>>([]),
    additionalSections: new FormArray<FormGroup<ResumeAdditionalSectionForm>>([]),
  });

  readonly previewPayload = computed(() => {
    this.formVersion();
    return this.buildPayload();
  });

  get skills(): FormArray<FormGroup<ResumeSkillGroupForm>> {
    return this.resumeForm.controls.skills;
  }

  get experience(): FormArray<FormGroup<ResumeExperienceItemForm>> {
    return this.resumeForm.controls.experience;
  }

  get education(): FormArray<FormGroup<ResumeEducationItemForm>> {
    return this.resumeForm.controls.education;
  }

  get languages(): FormArray<FormGroup<ResumeLanguageItemForm>> {
    return this.resumeForm.controls.languages;
  }

  get certifications(): FormArray<FormGroup<ResumeCertificationItemForm>> {
    return this.resumeForm.controls.certifications;
  }

  get additionalSections(): FormArray<FormGroup<ResumeAdditionalSectionForm>> {
    return this.resumeForm.controls.additionalSections;
  }

  ngOnInit(): void {
    this.resumeForm.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => {
      this.formVersion.update((version) => version + 1);
    });
    this.resumeForm.controls.language.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((language) => {
        if (isResumeLanguage(language)) {
          this.ensurePreviewLanguageBundle(language);
        }
      });
    this.loadResume();
  }

  loadResume(): void {
    if (this.resumeId === '') {
      this.error.set(createInvalidResumeIdError());
      return;
    }
    this.loading.set(true);
    this.error.set(null);
    this.resumeWorkspace
      .getResume(this.resumeId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (resume) => {
          this.populateForm(resume);
          this.loading.set(false);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
          this.notifications.error(this.i18n.translate('adminResumeWorkspace.loadError'));
        },
      });
  }

  setActiveTab(tab: ResumeEditorTab): void {
    this.activeTab.set(tab);
  }

  showPreview(): void {
    if (this.resumeForm.controls.language.invalid) {
      this.resumeForm.controls.language.markAsTouched();
      return;
    }
    this.ensurePreviewLanguageBundle(this.previewLanguage());
    this.formVersion.update((version) => version + 1);
    this.mode.set('preview');
  }

  showEdit(): void {
    this.mode.set('edit');
  }

  goBack(): void {
    this.router.navigateByUrl('/admin-panel/workspace/resumes');
  }

  saveResume(): void {
    if (this.resumeForm.invalid) {
      this.handleInvalidResumeForm();
      return;
    }
    const payload = this.buildPayload();
    this.saving.set(true);
    this.validationSubmitted.set(false);
    this.formError.set(null);
    this.resumeWorkspace
      .updateResume(this.resumeId, payload)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (resume) => {
          this.populateForm(resume);
          this.saving.set(false);
          this.notifications.success(this.i18n.translate('adminResumeWorkspace.saved'));
        },
        error: (err: ApiError) => {
          this.formError.set(err);
          this.saving.set(false);
          this.notifications.error(this.i18n.translate('adminResumeWorkspace.saveError'));
        },
      });
  }

  deleteResume(): void {
    const browserWindow = this.document.defaultView;
    if (!browserWindow?.confirm(this.i18n.translate('adminResumeWorkspace.confirmDelete'))) return;
    this.deleting.set(true);
    this.resumeWorkspace
      .deleteResume(this.resumeId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.deleting.set(false);
          this.notifications.success(this.i18n.translate('adminResumeWorkspace.deleted'));
          this.router.navigateByUrl('/admin-panel/workspace/resumes');
        },
        error: () => {
          this.deleting.set(false);
          this.notifications.error(this.i18n.translate('adminResumeWorkspace.deleteError'));
        },
      });
  }

  openExportModal(): void {
    this.exportError.set(null);
    this.selectedExportFormat.set('');
    this.exportModalOpen.set(true);
  }

  closeExportModal(): void {
    if (this.exporting()) return;
    this.exportModalOpen.set(false);
    this.exportError.set(null);
  }

  selectExportFormat(format: string): void {
    this.selectedExportFormat.set(isResumeExportFormat(format) ? format : '');
  }

  exportResume(): void {
    const format = this.selectedExportFormat();
    if (!isResumeExportFormat(format)) return;
    if (this.resumeForm.invalid) {
      this.exportModalOpen.set(false);
      this.handleInvalidResumeForm();
      return;
    }
    const payload = this.buildPayload();
    this.exporting.set(true);
    this.validationSubmitted.set(false);
    this.exportError.set(null);
    this.resumeWorkspace
      .exportResume(this.resumeId, format, payload)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (blob) => {
          this.downloadExport(blob, format);
          this.exporting.set(false);
          this.exportModalOpen.set(false);
          this.notifications.success(this.i18n.translate('adminResumeWorkspace.exported'));
        },
        error: (err: ApiError) => {
          this.exportError.set(err);
          this.exporting.set(false);
          this.notifications.error(this.i18n.translate('adminResumeWorkspace.exportError'));
        },
      });
  }

  addSkillGroup(): void {
    this.skills.push(this.createSkillGroupForm(createEmptyResumeSkillGroup()));
  }

  removeSkillGroup(index: number): void {
    this.skills.removeAt(index);
  }

  addSkillItem(skillIndex: number): void {
    this.addTextListItem(this.skillItems(skillIndex));
  }

  removeSkillItem(skillIndex: number, itemIndex: number): void {
    this.removeTextListItem(this.skillItems(skillIndex), itemIndex);
  }

  addExperienceItem(): void {
    this.experience.push(this.createExperienceItemForm(createEmptyResumeExperienceItem()));
  }

  removeExperienceItem(index: number): void {
    this.experience.removeAt(index);
  }

  addExperienceHighlight(experienceIndex: number): void {
    this.addTextListItem(this.experienceHighlights(experienceIndex));
  }

  removeExperienceHighlight(experienceIndex: number, itemIndex: number): void {
    this.removeTextListItem(this.experienceHighlights(experienceIndex), itemIndex);
  }

  addExperienceTechnology(experienceIndex: number): void {
    this.addTextListItem(this.experienceTechnologies(experienceIndex));
  }

  removeExperienceTechnology(experienceIndex: number, itemIndex: number): void {
    this.removeTextListItem(this.experienceTechnologies(experienceIndex), itemIndex);
  }

  addExperienceProject(experienceIndex: number): void {
    this.experienceProjects(experienceIndex).push(
      this.createProjectItemForm(createEmptyResumeProjectItem()),
    );
  }

  removeExperienceProject(experienceIndex: number, projectIndex: number): void {
    this.experienceProjects(experienceIndex).removeAt(projectIndex);
  }

  addProjectHighlight(experienceIndex: number, projectIndex: number): void {
    this.addTextListItem(this.projectHighlights(experienceIndex, projectIndex));
  }

  removeProjectHighlight(experienceIndex: number, projectIndex: number, itemIndex: number): void {
    this.removeTextListItem(this.projectHighlights(experienceIndex, projectIndex), itemIndex);
  }

  addProjectTechnology(experienceIndex: number, projectIndex: number): void {
    this.addTextListItem(this.projectTechnologies(experienceIndex, projectIndex));
  }

  removeProjectTechnology(experienceIndex: number, projectIndex: number, itemIndex: number): void {
    this.removeTextListItem(this.projectTechnologies(experienceIndex, projectIndex), itemIndex);
  }

  addEducationItem(): void {
    this.education.push(this.createEducationItemForm(createEmptyResumeEducationItem()));
  }

  removeEducationItem(index: number): void {
    this.education.removeAt(index);
  }

  addLanguageItem(): void {
    this.languages.push(this.createLanguageItemForm(createEmptyResumeLanguageItem()));
  }

  removeLanguageItem(index: number): void {
    this.languages.removeAt(index);
  }

  addCertificationItem(): void {
    this.certifications.push(
      this.createCertificationItemForm(createEmptyResumeCertificationItem()),
    );
  }

  removeCertificationItem(index: number): void {
    this.certifications.removeAt(index);
  }

  addAdditionalSection(): void {
    const section = createEmptyResumeAdditionalSection();
    this.additionalSections.push(
      this.createAdditionalSectionForm({
        ...section,
        items: [createEmptyResumeAdditionalSectionItem()],
      }),
    );
  }

  removeAdditionalSection(index: number): void {
    this.additionalSections.removeAt(index);
  }

  addAdditionalItem(sectionIndex: number): void {
    this.additionalItems(sectionIndex).push(
      this.createAdditionalSectionItemForm(createEmptyResumeAdditionalSectionItem()),
    );
  }

  removeAdditionalItem(sectionIndex: number, itemIndex: number): void {
    this.additionalItems(sectionIndex).removeAt(itemIndex);
  }

  skillItems(skillIndex: number): FormArray<TextControl> {
    return this.skills.at(skillIndex).controls.items;
  }

  experienceHighlights(experienceIndex: number): FormArray<TextControl> {
    return this.experience.at(experienceIndex).controls.highlights;
  }

  experienceTechnologies(experienceIndex: number): FormArray<TextControl> {
    return this.experience.at(experienceIndex).controls.technologies;
  }

  additionalItems(sectionIndex: number): FormArray<FormGroup<ResumeAdditionalSectionItemForm>> {
    return this.additionalSections.at(sectionIndex).controls.items;
  }

  experienceProjects(experienceIndex: number): FormArray<FormGroup<ResumeProjectItemForm>> {
    return this.experience.at(experienceIndex).controls.projects;
  }

  projectHighlights(experienceIndex: number, projectIndex: number): FormArray<TextControl> {
    return this.experienceProjects(experienceIndex).at(projectIndex).controls.highlights;
  }

  projectTechnologies(experienceIndex: number, projectIndex: number): FormArray<TextControl> {
    return this.experienceProjects(experienceIndex).at(projectIndex).controls.technologies;
  }

  previewMessage(key: string): string {
    return this.i18n.translateForLanguage(this.previewLanguage(), key);
  }

  previewText(value: string): string | null {
    return cleanPreviewText(value);
  }

  dateRange(
    startDate: string | null,
    endDate: string | null,
    currentStatus: ResumeCurrentStatus,
  ): string {
    const start = cleanNullableDateString(startDate);
    const end =
      currentStatus === 'current'
        ? this.previewMessage('adminResumeWorkspace.currentStatus.current')
        : cleanNullableDateString(endDate);
    return [start, end].filter(Boolean).join(' - ');
  }

  updateDate(control: NullableTextControl, value: string): void {
    control.setValue(value);
    control.markAsDirty();
    control.markAsTouched();
  }

  fieldInvalid(control: AbstractControl<unknown>): boolean {
    return controlInvalid(control, false);
  }

  fieldMessage(control: AbstractControl<unknown>): string | null {
    return validationMessage(control, this.i18n);
  }

  tabValidationIssueCount(tab: ResumeEditorTab): number {
    return this.validationIssues().filter((issue) => issue.tab === tab).length;
  }

  inlineListInputWidth(control: TextControl): string {
    const textWidth =
      cleanText(control.getRawValue()).length + INLINE_LIST_INPUT_EXTRA_TEXT_WIDTH_CH;
    const width = Math.min(
      Math.max(textWidth, INLINE_LIST_INPUT_MIN_TEXT_WIDTH_CH),
      INLINE_LIST_INPUT_MAX_TEXT_WIDTH_CH,
    );
    return `calc(${width}ch + ${INLINE_LIST_INPUT_ACTION_WIDTH_REM}rem)`;
  }

  hasSummary(content: ResumeContent): boolean {
    return Boolean(this.previewText(content.summary.text));
  }

  buildPayload(): ResumePayload {
    const title = this.resumeForm.controls.title.getRawValue().trim();
    return {
      title,
      language: toResumeLanguage(this.resumeForm.controls.language.getRawValue()),
      content: {
        profile: this.buildProfile(),
        summary: this.buildSummary(),
        skills: this.skills.controls.map((control) => this.buildSkillGroup(control)),
        experience: this.experience.controls.map((control) => this.buildExperienceItem(control)),
        education: this.education.controls.map((control) => this.buildEducationItem(control)),
        languages: this.languages.controls.map((control) => this.buildLanguageItem(control)),
        certifications: this.certifications.controls.map((control) =>
          this.buildCertificationItem(control),
        ),
        additionalSections: this.additionalSections.controls.map((control) =>
          this.buildAdditionalSection(control),
        ),
      },
    };
  }

  private populateForm(resume: Resume): void {
    this.validationSubmitted.set(false);
    this.resumeForm.controls.title.setValue(resume.title, { emitEvent: false });
    this.resumeForm.controls.language.setValue(resume.language, { emitEvent: false });
    this.resumeForm.setControl('profile', this.createProfileForm(resume.content.profile), {
      emitEvent: false,
    });
    this.resumeForm.setControl('summary', this.createSummaryForm(resume.content.summary), {
      emitEvent: false,
    });
    this.replaceFormArray(
      this.skills,
      resume.content.skills.map((item) => this.createSkillGroupForm(item)),
    );
    this.replaceFormArray(
      this.experience,
      resume.content.experience.map((item) => this.createExperienceItemForm(item)),
    );
    this.replaceFormArray(
      this.education,
      resume.content.education.map((item) => this.createEducationItemForm(item)),
    );
    this.replaceFormArray(
      this.languages,
      resume.content.languages.map((item) => this.createLanguageItemForm(item)),
    );
    this.replaceFormArray(
      this.certifications,
      resume.content.certifications.map((item) => this.createCertificationItemForm(item)),
    );
    this.replaceFormArray(
      this.additionalSections,
      resume.content.additionalSections.map((item) => this.createAdditionalSectionForm(item)),
    );
    this.ensurePreviewLanguageBundle(resume.language);
    this.formVersion.update((version) => version + 1);
  }

  private handleInvalidResumeForm(): void {
    this.resumeForm.markAllAsTouched();
    const issues = this.collectValidationIssues();
    this.validationSubmitted.set(true);
    this.mode.set('edit');
    const firstIssue = issues.at(0) ?? null;
    if (firstIssue?.tab !== null && firstIssue?.tab !== undefined) {
      this.activeTab.set(firstIssue.tab);
    }
    this.notifications.error(this.validationNotificationMessage(firstIssue));
  }

  private validationNotificationMessage(firstIssue: ResumeValidationIssue | null): string {
    if (firstIssue === null) {
      return this.i18n.translate('adminResumeWorkspace.validationError');
    }
    return this.i18n.translate('adminResumeWorkspace.validationErrorWithFirstIssue', {
      issue: firstIssue.message,
    });
  }

  private collectValidationIssues(): ResumeValidationIssue[] {
    const issues: ResumeValidationIssue[] = [];
    this.addControlValidationIssue(
      issues,
      null,
      [this.fieldLabel('title')],
      this.resumeForm.controls.title,
    );
    this.addControlValidationIssue(
      issues,
      null,
      [this.fieldLabel('language')],
      this.resumeForm.controls.language,
    );
    this.collectProfileValidationIssues(issues);
    this.collectSummaryValidationIssues(issues);
    this.collectSkillsValidationIssues(issues);
    this.collectExperienceValidationIssues(issues);
    this.collectEducationValidationIssues(issues);
    this.collectLanguagesValidationIssues(issues);
    this.collectCertificationsValidationIssues(issues);
    this.collectAdditionalSectionsValidationIssues(issues);
    return issues;
  }

  private collectProfileValidationIssues(issues: ResumeValidationIssue[]): void {
    const controls = this.resumeForm.controls.profile.controls;
    const path = [this.tabLabel('profile')];
    this.addControlValidationIssue(
      issues,
      'profile',
      [...path, this.fieldLabel('fullName')],
      controls.fullName,
    );
    this.addControlValidationIssue(
      issues,
      'profile',
      [...path, this.fieldLabel('email')],
      controls.email,
    );
    this.addControlValidationIssue(
      issues,
      'profile',
      [...path, this.fieldLabel('role')],
      controls.role,
    );
    this.addControlValidationIssue(
      issues,
      'profile',
      [...path, this.fieldLabel('location')],
      controls.location,
    );
    this.addControlValidationIssue(
      issues,
      'profile',
      [...path, this.fieldLabel('phone')],
      controls.phone,
    );
    this.addControlValidationIssue(
      issues,
      'profile',
      [...path, this.fieldLabel('websiteUrl')],
      controls.websiteUrl,
    );
    this.addControlValidationIssue(
      issues,
      'profile',
      [...path, this.fieldLabel('linkedinUrl')],
      controls.linkedinUrl,
    );
    this.addControlValidationIssue(
      issues,
      'profile',
      [...path, this.fieldLabel('githubUrl')],
      controls.githubUrl,
    );
    this.addControlValidationIssue(
      issues,
      'profile',
      [...path, this.fieldLabel('telegram')],
      controls.telegram,
    );
  }

  private collectSummaryValidationIssues(issues: ResumeValidationIssue[]): void {
    this.addControlValidationIssue(
      issues,
      'summary',
      [this.tabLabel('summary'), this.fieldLabel('summary')],
      this.resumeForm.controls.summary.controls.text,
    );
  }

  private collectSkillsValidationIssues(issues: ResumeValidationIssue[]): void {
    const tabPath = [this.tabLabel('skills')];
    this.skills.controls.forEach((skillGroup, skillIndex) => {
      const skillPath = [...tabPath, this.entryLabel('skillGroup', skillIndex)];
      this.addControlValidationIssue(
        issues,
        'skills',
        [...skillPath, this.fieldLabel('category')],
        skillGroup.controls.category,
      );
      skillGroup.controls.items.controls.forEach((itemControl, itemIndex) => {
        this.addControlValidationIssue(
          issues,
          'skills',
          [...skillPath, this.listItemLabel(itemIndex)],
          itemControl,
        );
      });
    });
  }

  private collectExperienceValidationIssues(issues: ResumeValidationIssue[]): void {
    const tabPath = [this.tabLabel('experience')];
    this.experience.controls.forEach((experienceItem, experienceIndex) => {
      const experiencePath = [...tabPath, this.entryLabel('company', experienceIndex)];
      const controls = experienceItem.controls;
      this.addControlValidationIssue(
        issues,
        'experience',
        [...experiencePath, this.fieldLabel('company')],
        controls.company,
      );
      this.addControlValidationIssue(
        issues,
        'experience',
        [...experiencePath, this.fieldLabel('position')],
        controls.position,
      );
      this.addControlValidationIssue(
        issues,
        'experience',
        [...experiencePath, this.fieldLabel('location')],
        controls.location,
      );
      this.addControlValidationIssue(
        issues,
        'experience',
        [...experiencePath, this.fieldLabel('startDate')],
        controls.startDate,
      );
      this.addControlValidationIssue(
        issues,
        'experience',
        [...experiencePath, this.fieldLabel('endDate')],
        controls.endDate,
      );
      this.addControlValidationIssue(
        issues,
        'experience',
        [...experiencePath, this.fieldLabel('summary')],
        controls.summary,
      );
      controls.highlights.controls.forEach((highlightControl, itemIndex) => {
        this.addControlValidationIssue(
          issues,
          'experience',
          [...experiencePath, this.fieldLabel('highlights'), this.listItemLabel(itemIndex)],
          highlightControl,
        );
      });
      controls.technologies.controls.forEach((technologyControl, itemIndex) => {
        this.addControlValidationIssue(
          issues,
          'experience',
          [...experiencePath, this.fieldLabel('technologies'), this.listItemLabel(itemIndex)],
          technologyControl,
        );
      });
      controls.projects.controls.forEach((projectControl, projectIndex) => {
        this.collectProjectValidationIssues(issues, experiencePath, projectControl, projectIndex);
      });
    });
  }

  private collectProjectValidationIssues(
    issues: ResumeValidationIssue[],
    experiencePath: string[],
    projectControl: FormGroup<ResumeProjectItemForm>,
    projectIndex: number,
  ): void {
    const projectPath = [...experiencePath, this.entryLabel('project', projectIndex)];
    const controls = projectControl.controls;
    this.addControlValidationIssue(
      issues,
      'experience',
      [...projectPath, this.fieldLabel('projectName')],
      controls.name,
    );
    this.addControlValidationIssue(
      issues,
      'experience',
      [...projectPath, this.fieldLabel('role')],
      controls.role,
    );
    this.addControlValidationIssue(
      issues,
      'experience',
      [...projectPath, this.fieldLabel('description')],
      controls.description,
    );
    controls.highlights.controls.forEach((highlightControl, itemIndex) => {
      this.addControlValidationIssue(
        issues,
        'experience',
        [...projectPath, this.fieldLabel('highlights'), this.listItemLabel(itemIndex)],
        highlightControl,
      );
    });
    controls.technologies.controls.forEach((technologyControl, itemIndex) => {
      this.addControlValidationIssue(
        issues,
        'experience',
        [...projectPath, this.fieldLabel('technologies'), this.listItemLabel(itemIndex)],
        technologyControl,
      );
    });
    this.addControlValidationIssue(
      issues,
      'experience',
      [...projectPath, this.fieldLabel('url')],
      controls.url,
    );
  }

  private collectEducationValidationIssues(issues: ResumeValidationIssue[]): void {
    const tabPath = [this.tabLabel('education')];
    this.education.controls.forEach((educationItem, educationIndex) => {
      const educationPath = [...tabPath, this.entryLabel('education', educationIndex)];
      const controls = educationItem.controls;
      this.addControlValidationIssue(
        issues,
        'education',
        [...educationPath, this.fieldLabel('institution')],
        controls.institution,
      );
      this.addControlValidationIssue(
        issues,
        'education',
        [...educationPath, this.fieldLabel('degree')],
        controls.degree,
      );
      this.addControlValidationIssue(
        issues,
        'education',
        [...educationPath, this.fieldLabel('field')],
        controls.field,
      );
      this.addControlValidationIssue(
        issues,
        'education',
        [...educationPath, this.fieldLabel('location')],
        controls.location,
      );
      this.addControlValidationIssue(
        issues,
        'education',
        [...educationPath, this.fieldLabel('startDate')],
        controls.startDate,
      );
      this.addControlValidationIssue(
        issues,
        'education',
        [...educationPath, this.fieldLabel('endDate')],
        controls.endDate,
      );
      this.addControlValidationIssue(
        issues,
        'education',
        [...educationPath, this.fieldLabel('description')],
        controls.description,
      );
    });
  }

  private collectLanguagesValidationIssues(issues: ResumeValidationIssue[]): void {
    const tabPath = [this.tabLabel('languages')];
    this.languages.controls.forEach((languageItem, languageIndex) => {
      const languagePath = [...tabPath, this.entryLabel('language', languageIndex)];
      this.addControlValidationIssue(
        issues,
        'languages',
        [...languagePath, this.fieldLabel('languageName')],
        languageItem.controls.name,
      );
      this.addControlValidationIssue(
        issues,
        'languages',
        [...languagePath, this.fieldLabel('proficiency')],
        languageItem.controls.proficiency,
      );
    });
  }

  private collectCertificationsValidationIssues(issues: ResumeValidationIssue[]): void {
    const tabPath = [this.tabLabel('certifications')];
    this.certifications.controls.forEach((certification, certificationIndex) => {
      const certificationPath = [...tabPath, this.entryLabel('certification', certificationIndex)];
      const controls = certification.controls;
      this.addControlValidationIssue(
        issues,
        'certifications',
        [...certificationPath, this.fieldLabel('certificationName')],
        controls.name,
      );
      this.addControlValidationIssue(
        issues,
        'certifications',
        [...certificationPath, this.fieldLabel('issuer')],
        controls.issuer,
      );
      this.addControlValidationIssue(
        issues,
        'certifications',
        [...certificationPath, this.fieldLabel('issuedOn')],
        controls.issuedOn,
      );
      this.addControlValidationIssue(
        issues,
        'certifications',
        [...certificationPath, this.fieldLabel('expiresOn')],
        controls.expiresOn,
      );
      this.addControlValidationIssue(
        issues,
        'certifications',
        [...certificationPath, this.fieldLabel('credentialUrl')],
        controls.credentialUrl,
      );
    });
  }

  private collectAdditionalSectionsValidationIssues(issues: ResumeValidationIssue[]): void {
    const tabPath = [this.tabLabel('additional')];
    this.additionalSections.controls.forEach((section, sectionIndex) => {
      const sectionPath = [...tabPath, this.entryLabel('additionalSection', sectionIndex)];
      this.addControlValidationIssue(
        issues,
        'additional',
        [...sectionPath, this.fieldLabel('sectionTitle')],
        section.controls.title,
      );
      if (section.controls.items.errors !== null) {
        this.addControlValidationIssue(
          issues,
          'additional',
          [...sectionPath, this.fieldLabel('items')],
          section.controls.items,
        );
      }
      section.controls.items.controls.forEach((item, itemIndex) => {
        const itemPath = [...sectionPath, this.entryLabel('additionalItem', itemIndex)];
        this.addControlValidationIssue(
          issues,
          'additional',
          [...itemPath, this.fieldLabel('itemTitle')],
          item.controls.title,
        );
        this.addControlValidationIssue(
          issues,
          'additional',
          [...itemPath, this.fieldLabel('url')],
          item.controls.url,
        );
        this.addControlValidationIssue(
          issues,
          'additional',
          [...itemPath, this.fieldLabel('description')],
          item.controls.description,
        );
      });
    });
  }

  private addControlValidationIssue(
    issues: ResumeValidationIssue[],
    tab: ResumeEditorTab | null,
    path: string[],
    control: AbstractControl<unknown>,
  ): void {
    if (control.valid) return;
    const message = this.fieldMessage(control) ?? this.i18n.translate('validation.invalid');
    issues.push({
      tab,
      message: this.i18n.translate('adminResumeWorkspace.validationIssue', {
        field: path.join(this.i18n.translate('adminResumeWorkspace.validationPathSeparator')),
        message,
      }),
    });
  }

  private tabLabel(tab: ResumeEditorTab): string {
    const tabDefinition = RESUME_EDITOR_TABS.find((item) => item.key === tab);
    if (tabDefinition === undefined) {
      throw new Error(`Unsupported resume editor tab: ${tab}`);
    }
    return this.i18n.translate(tabDefinition.labelKey);
  }

  private fieldLabel(key: string): string {
    return this.i18n.translate(`adminResumeWorkspace.field.${key}`);
  }

  private entryLabel(key: string, index: number): string {
    return this.i18n.translate(`adminResumeWorkspace.entry.${key}`, { index: index + 1 });
  }

  private listItemLabel(index: number): string {
    return this.i18n.translate('adminResumeWorkspace.validationListItem', { index: index + 1 });
  }

  private replaceFormArray<TControl extends AbstractControl>(
    formArray: FormArray<TControl>,
    controls: TControl[],
  ): void {
    while (formArray.length > 0) {
      formArray.removeAt(0, { emitEvent: false });
    }
    for (const control of controls) {
      formArray.push(control, { emitEvent: false });
    }
  }

  private createProfileForm(profile: ResumeProfile): FormGroup<ResumeProfileForm> {
    return new FormGroup<ResumeProfileForm>({
      fullName: this.requiredText(profile.fullName, ADMIN_VALIDATION_LIMITS.shortText),
      role: this.requiredText(profile.role, ADMIN_VALIDATION_LIMITS.shortText),
      location: this.text(profile.location, ADMIN_VALIDATION_LIMITS.shortText),
      email: this.textWithValidators(profile.email, ADMIN_VALIDATION_LIMITS.email, [
        emailValidator,
      ]),
      phone: this.text(profile.phone, 255),
      websiteUrl: this.urlText(profile.websiteUrl),
      linkedinUrl: this.urlText(profile.linkedinUrl),
      githubUrl: this.urlText(profile.githubUrl),
      telegram: this.text(profile.telegram, ADMIN_VALIDATION_LIMITS.shortText),
    });
  }

  private createSummaryForm(summary: ResumeSummary): FormGroup<ResumeSummaryForm> {
    return new FormGroup<ResumeSummaryForm>({
      text: this.text(summary.text, ADMIN_VALIDATION_LIMITS.resumeLongText),
    });
  }

  private createSkillGroupForm(skill: ResumeSkillGroup): FormGroup<ResumeSkillGroupForm> {
    return new FormGroup<ResumeSkillGroupForm>({
      category: this.requiredText(skill.category, ADMIN_VALIDATION_LIMITS.shortText),
      items: this.createTextListForm(skill.items),
    });
  }

  private createExperienceItemForm(
    item: ResumeExperienceItem,
  ): FormGroup<ResumeExperienceItemForm> {
    return new FormGroup<ResumeExperienceItemForm>({
      company: this.requiredText(item.company, ADMIN_VALIDATION_LIMITS.shortText),
      position: this.requiredText(item.position, ADMIN_VALIDATION_LIMITS.shortText),
      location: this.text(item.location, ADMIN_VALIDATION_LIMITS.shortText),
      startDate: this.requiredNullableText(item.startDate, 32),
      endDate: this.nullableText(item.endDate, 32),
      currentStatus: this.currentStatus(item.currentStatus),
      summary: this.text(item.summary, ADMIN_VALIDATION_LIMITS.resumeLongText),
      highlights: this.createTextListForm(item.highlights),
      technologies: this.createTextListForm(item.technologies),
      projects: new FormArray<FormGroup<ResumeProjectItemForm>>(
        item.projects.map((project) => this.createProjectItemForm(project)),
      ),
    });
  }

  private createProjectItemForm(item: ResumeProjectItem): FormGroup<ResumeProjectItemForm> {
    return new FormGroup<ResumeProjectItemForm>({
      name: this.requiredText(item.name, ADMIN_VALIDATION_LIMITS.shortText),
      role: this.requiredText(item.role, ADMIN_VALIDATION_LIMITS.shortText),
      description: this.text(item.description, ADMIN_VALIDATION_LIMITS.resumeLongText),
      highlights: this.createTextListForm(item.highlights),
      technologies: this.createTextListForm(item.technologies),
      url: this.urlText(item.url),
    });
  }

  private createEducationItemForm(item: ResumeEducationItem): FormGroup<ResumeEducationItemForm> {
    return new FormGroup<ResumeEducationItemForm>({
      institution: this.requiredText(item.institution, ADMIN_VALIDATION_LIMITS.shortText),
      degree: this.requiredText(item.degree, ADMIN_VALIDATION_LIMITS.shortText),
      field: this.requiredText(item.field, ADMIN_VALIDATION_LIMITS.shortText),
      location: this.requiredText(item.location, ADMIN_VALIDATION_LIMITS.shortText),
      startDate: this.requiredNullableText(item.startDate, 32),
      endDate: this.requiredNullableText(item.endDate, 32),
      description: this.text(item.description, ADMIN_VALIDATION_LIMITS.resumeLongText),
    });
  }

  private createLanguageItemForm(item: ResumeLanguageItem): FormGroup<ResumeLanguageItemForm> {
    return new FormGroup<ResumeLanguageItemForm>({
      name: this.requiredText(item.name, ADMIN_VALIDATION_LIMITS.shortText),
      proficiency: this.requiredText(item.proficiency, ADMIN_VALIDATION_LIMITS.shortText),
    });
  }

  private createCertificationItemForm(
    item: ResumeCertificationItem,
  ): FormGroup<ResumeCertificationItemForm> {
    return new FormGroup<ResumeCertificationItemForm>({
      name: this.requiredText(item.name, ADMIN_VALIDATION_LIMITS.shortText),
      issuer: this.text(item.issuer, ADMIN_VALIDATION_LIMITS.shortText),
      issuedOn: this.nullableText(item.issuedOn, 32),
      expiresOn: this.nullableText(item.expiresOn, 32),
      credentialUrl: this.urlText(item.credentialUrl),
    });
  }

  private createAdditionalSectionForm(
    section: ResumeAdditionalSection,
  ): FormGroup<ResumeAdditionalSectionForm> {
    return new FormGroup<ResumeAdditionalSectionForm>({
      title: this.requiredText(section.title, ADMIN_VALIDATION_LIMITS.shortText),
      items: new FormArray<FormGroup<ResumeAdditionalSectionItemForm>>(
        section.items.map((item) => this.createAdditionalSectionItemForm(item)),
        { validators: nonEmptyFormArray },
      ),
    });
  }

  private createAdditionalSectionItemForm(
    item: ResumeAdditionalSectionItem,
  ): FormGroup<ResumeAdditionalSectionItemForm> {
    return new FormGroup<ResumeAdditionalSectionItemForm>({
      title: this.requiredText(item.title, ADMIN_VALIDATION_LIMITS.shortText),
      description: this.text(item.description, ADMIN_VALIDATION_LIMITS.resumeLongText),
      url: this.urlText(item.url),
    });
  }

  private text(value: string, maxLength: number | null): TextControl {
    if (maxLength === null) return this.formBuilder.control(value);
    return this.formBuilder.control(value, { validators: Validators.maxLength(maxLength) });
  }

  private requiredText(value: string, maxLength: number): TextControl {
    return this.textWithValidators(value, maxLength, [trimRequired]);
  }

  private textWithValidators(
    value: string,
    maxLength: number,
    validators: ValidatorFn[],
  ): TextControl {
    return this.formBuilder.control(value, {
      validators: [Validators.maxLength(maxLength), ...validators],
    });
  }

  private urlText(value: string): TextControl {
    return this.textWithValidators(value, ADMIN_VALIDATION_LIMITS.url, [httpUrlValidator]);
  }

  private nullableText(value: string | null, maxLength: number | null): NullableTextControl {
    if (maxLength === null) return new FormControl<string | null>(value);
    return new FormControl<string | null>(value, { validators: Validators.maxLength(maxLength) });
  }

  private requiredNullableText(value: string | null, maxLength: number): NullableTextControl {
    return new FormControl<string | null>(value, {
      validators: [nullableTrimRequired, Validators.maxLength(maxLength)],
    });
  }

  private currentStatus(value: ResumeCurrentStatus): CurrentStatusControl {
    return this.formBuilder.control(value);
  }

  private createTextListForm(values: string[]): FormArray<TextControl> {
    return new FormArray<TextControl>(values.map((value) => this.listText(value)));
  }

  private listText(value: string): TextControl {
    return this.requiredText(value, ADMIN_VALIDATION_LIMITS.shortText);
  }

  private addTextListItem(list: FormArray<TextControl>): void {
    list.push(this.listText(''));
  }

  private removeTextListItem(list: FormArray<TextControl>, index: number): void {
    list.removeAt(index);
  }

  private buildProfile(): ResumeProfile {
    const value = this.resumeForm.controls.profile.getRawValue();
    return {
      fullName: cleanText(value.fullName),
      role: cleanText(value.role),
      location: cleanText(value.location),
      email: cleanText(value.email),
      phone: cleanText(value.phone),
      websiteUrl: cleanText(value.websiteUrl),
      linkedinUrl: cleanText(value.linkedinUrl),
      githubUrl: cleanText(value.githubUrl),
      telegram: cleanText(value.telegram),
    };
  }

  private buildSummary(): ResumeSummary {
    const value = this.resumeForm.controls.summary.getRawValue();
    return {
      text: cleanText(value.text),
    };
  }

  private buildSkillGroup(control: FormGroup<ResumeSkillGroupForm>): ResumeSkillGroup {
    const value = control.getRawValue();
    return {
      category: cleanText(value.category),
      items: this.buildTextList(control.controls.items),
    };
  }

  private buildExperienceItem(control: FormGroup<ResumeExperienceItemForm>): ResumeExperienceItem {
    const value = control.getRawValue();
    return {
      company: cleanText(value.company),
      position: cleanText(value.position),
      location: cleanText(value.location),
      startDate: cleanNullableDateString(value.startDate),
      endDate: cleanNullableDateString(value.endDate),
      currentStatus: value.currentStatus,
      summary: cleanText(value.summary),
      highlights: this.buildTextList(control.controls.highlights),
      technologies: this.buildTextList(control.controls.technologies),
      projects: control.controls.projects.controls.map((projectControl) =>
        this.buildProjectItem(projectControl),
      ),
    };
  }

  private buildProjectItem(control: FormGroup<ResumeProjectItemForm>): ResumeProjectItem {
    const value = control.getRawValue();
    return {
      name: cleanText(value.name),
      role: cleanText(value.role),
      description: cleanText(value.description),
      highlights: this.buildTextList(control.controls.highlights),
      technologies: this.buildTextList(control.controls.technologies),
      url: cleanText(value.url),
    };
  }

  private buildTextList(control: FormArray<TextControl>): string[] {
    return control
      .getRawValue()
      .map((line) => cleanText(line))
      .filter((line) => line.length > 0);
  }

  private buildEducationItem(control: FormGroup<ResumeEducationItemForm>): ResumeEducationItem {
    const value = control.getRawValue();
    return {
      institution: cleanText(value.institution),
      degree: cleanText(value.degree),
      field: cleanText(value.field),
      location: cleanText(value.location),
      startDate: cleanNullableDateString(value.startDate),
      endDate: cleanNullableDateString(value.endDate),
      description: cleanText(value.description),
    };
  }

  private buildLanguageItem(control: FormGroup<ResumeLanguageItemForm>): ResumeLanguageItem {
    const value = control.getRawValue();
    return {
      name: cleanText(value.name),
      proficiency: cleanText(value.proficiency),
    };
  }

  private buildCertificationItem(
    control: FormGroup<ResumeCertificationItemForm>,
  ): ResumeCertificationItem {
    const value = control.getRawValue();
    return {
      name: cleanText(value.name),
      issuer: cleanText(value.issuer),
      issuedOn: cleanNullableDateString(value.issuedOn),
      expiresOn: cleanNullableDateString(value.expiresOn),
      credentialUrl: cleanText(value.credentialUrl),
    };
  }

  private buildAdditionalSection(
    control: FormGroup<ResumeAdditionalSectionForm>,
  ): ResumeAdditionalSection {
    const value = control.getRawValue();
    return {
      title: cleanText(value.title),
      items: control.controls.items.controls.map((itemControl) =>
        this.buildAdditionalSectionItem(itemControl),
      ),
    };
  }

  private buildAdditionalSectionItem(
    control: FormGroup<ResumeAdditionalSectionItemForm>,
  ): ResumeAdditionalSectionItem {
    const value = control.getRawValue();
    return {
      title: cleanText(value.title),
      description: cleanText(value.description),
      url: cleanText(value.url),
    };
  }

  private ensurePreviewLanguageBundle(language: ResumeLanguage): void {
    this.i18n
      .ensureLanguageBundle(language)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        catchError(() => EMPTY),
      )
      .subscribe(() => {
        this.formVersion.update((version) => version + 1);
      });
  }

  private resolveResumeId(): string {
    return this.route.snapshot.paramMap.get('id') ?? '';
  }

  private downloadExport(blob: Blob, format: ResumeExportFormat): void {
    const browserWindow = this.document.defaultView;
    if (!browserWindow) return;
    const objectUrl = browserWindow.URL.createObjectURL(blob);
    const anchor = this.document.createElement('a');
    anchor.href = objectUrl;
    anchor.download = `resume-${this.resumeId}.${format}`;
    anchor.rel = 'noopener';
    try {
      this.document.body.append(anchor);
      anchor.click();
      anchor.remove();
    } finally {
      browserWindow.URL.revokeObjectURL(objectUrl);
    }
  }
}

function cleanText(value: string): string {
  return value.trim();
}

function cleanPreviewText(value: string): string | null {
  const trimmed = cleanText(value);
  return trimmed.length > 0 ? trimmed : null;
}

function cleanNullableDateString(value: string | null): string | null {
  const trimmed = value?.trim() ?? '';
  return trimmed.length > 0 ? trimmed : null;
}

function nullableTrimRequired(control: AbstractControl<string | null>): ValidationErrors | null {
  return (control.value ?? '').trim() === '' ? { required: true } : null;
}

function nonEmptyFormArray(control: AbstractControl<unknown>): ValidationErrors | null {
  return Array.isArray(control.value) && control.value.length > 0 ? null : { required: true };
}

function isResumeLanguage(value: string): value is ResumeLanguage {
  return value === 'ru' || value === 'en';
}

function isResumeExportFormat(value: string): value is ResumeExportFormat {
  return value === 'pdf' || value === 'docx';
}

function toResumeLanguage(value: string): ResumeLanguage {
  if (isResumeLanguage(value)) return value;
  throw new Error(`Unsupported resume language: ${value}`);
}

function createInvalidResumeIdError(): ApiError {
  return {
    code: 'bad_request',
    type: 'BadRequest',
    message: 'Invalid resume id',
    location: null,
    attr: null,
  };
}

function createEmptyResumeProfile(): ResumeProfile {
  return {
    fullName: '',
    role: '',
    location: '',
    email: '',
    phone: '',
    websiteUrl: '',
    linkedinUrl: '',
    githubUrl: '',
    telegram: '',
  };
}

function createEmptyResumeSummary(): ResumeSummary {
  return {
    text: '',
  };
}

function createEmptyResumeSkillGroup(): ResumeSkillGroup {
  return {
    category: '',
    items: [],
  };
}

function createEmptyResumeExperienceItem(): ResumeExperienceItem {
  return {
    company: '',
    position: '',
    location: '',
    startDate: null,
    endDate: null,
    currentStatus: 'notSet',
    summary: '',
    highlights: [],
    technologies: [],
    projects: [],
  };
}

function createEmptyResumeProjectItem(): ResumeProjectItem {
  return {
    name: '',
    role: '',
    description: '',
    highlights: [],
    technologies: [],
    url: '',
  };
}

function createEmptyResumeEducationItem(): ResumeEducationItem {
  return {
    institution: '',
    degree: '',
    field: '',
    location: '',
    startDate: null,
    endDate: null,
    description: '',
  };
}

function createEmptyResumeLanguageItem(): ResumeLanguageItem {
  return {
    name: '',
    proficiency: '',
  };
}

function createEmptyResumeCertificationItem(): ResumeCertificationItem {
  return {
    name: '',
    issuer: '',
    issuedOn: null,
    expiresOn: null,
    credentialUrl: '',
  };
}

function createEmptyResumeAdditionalSection(): ResumeAdditionalSection {
  return {
    title: '',
    items: [],
  };
}

function createEmptyResumeAdditionalSectionItem(): ResumeAdditionalSectionItem {
  return {
    title: '',
    description: '',
    url: '',
  };
}
