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
import {
  AbstractControl,
  FormArray,
  FormControl,
  FormGroup,
  NonNullableFormBuilder,
  ReactiveFormsModule,
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
import {
  Resume,
  ResumeAdditionalSection,
  ResumeAdditionalSectionItem,
  ResumeCertificationItem,
  ResumeContent,
  ResumeCurrentStatus,
  ResumeEducationItem,
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
  itemsText: TextControl;
}

interface ResumeExperienceItemForm {
  company: TextControl;
  position: TextControl;
  location: TextControl;
  startDate: NullableTextControl;
  endDate: NullableTextControl;
  currentStatus: CurrentStatusControl;
  summary: TextControl;
  highlightsText: TextControl;
  technologiesText: TextControl;
  projects: FormArray<FormGroup<ResumeProjectItemForm>>;
}

interface ResumeProjectItemForm {
  name: TextControl;
  role: TextControl;
  description: TextControl;
  highlightsText: TextControl;
  technologiesText: TextControl;
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

@Component({
  selector: 'app-admin-resume-detail-page',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    TranslatePipe,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    LocalizedDatePickerComponent,
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
  private readonly resumeId = this.resolveResumeId();

  readonly tabs = RESUME_EDITOR_TABS;
  readonly currentStatusOptions = RESUME_CURRENT_STATUS_OPTIONS;
  readonly languageOptions = RESUME_LANGUAGE_OPTIONS;
  readonly activeTab = signal<ResumeEditorTab>('profile');
  readonly mode = signal<ResumeEditorMode>('edit');
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
  readonly error = signal<ApiError | null>(null);
  readonly formError = signal<ApiError | null>(null);
  readonly formVersion = signal(0);

  readonly resumeForm = new FormGroup<ResumeEditorForm>({
    title: this.formBuilder.control('', {
      validators: [Validators.required, Validators.maxLength(255)],
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
    if (this.resumeId <= 0) {
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
      this.resumeForm.markAllAsTouched();
      return;
    }
    const payload = this.buildPayload();
    this.saving.set(true);
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
    if (!window.confirm(this.i18n.translate('adminResumeWorkspace.confirmDelete'))) return;
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

  addSkillGroup(): void {
    this.skills.push(this.createSkillGroupForm(createEmptyResumeSkillGroup()));
  }

  removeSkillGroup(index: number): void {
    this.skills.removeAt(index);
  }

  addExperienceItem(): void {
    this.experience.push(this.createExperienceItemForm(createEmptyResumeExperienceItem()));
  }

  removeExperienceItem(index: number): void {
    this.experience.removeAt(index);
  }

  addExperienceProject(experienceIndex: number): void {
    this.experienceProjects(experienceIndex).push(
      this.createProjectItemForm(createEmptyResumeProjectItem()),
    );
  }

  removeExperienceProject(experienceIndex: number, projectIndex: number): void {
    this.experienceProjects(experienceIndex).removeAt(projectIndex);
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
    this.additionalSections.push(
      this.createAdditionalSectionForm(createEmptyResumeAdditionalSection()),
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

  additionalItems(sectionIndex: number): FormArray<FormGroup<ResumeAdditionalSectionItemForm>> {
    return this.additionalSections.at(sectionIndex).controls.items;
  }

  experienceProjects(experienceIndex: number): FormArray<FormGroup<ResumeProjectItemForm>> {
    return this.experience.at(experienceIndex).controls.projects;
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
      fullName: this.text(profile.fullName, 255),
      role: this.text(profile.role, 255),
      location: this.text(profile.location, 255),
      email: this.text(profile.email, 255),
      phone: this.text(profile.phone, 255),
      websiteUrl: this.text(profile.websiteUrl, 512),
      linkedinUrl: this.text(profile.linkedinUrl, 512),
      githubUrl: this.text(profile.githubUrl, 512),
      telegram: this.text(profile.telegram, 255),
    });
  }

  private createSummaryForm(summary: ResumeSummary): FormGroup<ResumeSummaryForm> {
    return new FormGroup<ResumeSummaryForm>({
      text: this.text(summary.text, null),
    });
  }

  private createSkillGroupForm(skill: ResumeSkillGroup): FormGroup<ResumeSkillGroupForm> {
    return new FormGroup<ResumeSkillGroupForm>({
      category: this.text(skill.category, 255),
      itemsText: this.text(linesToText(skill.items), null),
    });
  }

  private createExperienceItemForm(
    item: ResumeExperienceItem,
  ): FormGroup<ResumeExperienceItemForm> {
    return new FormGroup<ResumeExperienceItemForm>({
      company: this.text(item.company, 255),
      position: this.text(item.position, 255),
      location: this.text(item.location, 255),
      startDate: this.nullableText(item.startDate, 32),
      endDate: this.nullableText(item.endDate, 32),
      currentStatus: this.currentStatus(item.currentStatus),
      summary: this.text(item.summary, null),
      highlightsText: this.text(linesToText(item.highlights), null),
      technologiesText: this.text(linesToText(item.technologies), null),
      projects: new FormArray<FormGroup<ResumeProjectItemForm>>(
        item.projects.map((project) => this.createProjectItemForm(project)),
      ),
    });
  }

  private createProjectItemForm(item: ResumeProjectItem): FormGroup<ResumeProjectItemForm> {
    return new FormGroup<ResumeProjectItemForm>({
      name: this.text(item.name, 255),
      role: this.text(item.role, 255),
      description: this.text(item.description, null),
      highlightsText: this.text(linesToText(item.highlights), null),
      technologiesText: this.text(linesToText(item.technologies), null),
      url: this.text(item.url, 512),
    });
  }

  private createEducationItemForm(item: ResumeEducationItem): FormGroup<ResumeEducationItemForm> {
    return new FormGroup<ResumeEducationItemForm>({
      institution: this.text(item.institution, 255),
      degree: this.text(item.degree, 255),
      field: this.text(item.field, 255),
      location: this.text(item.location, 255),
      startDate: this.nullableText(item.startDate, 32),
      endDate: this.nullableText(item.endDate, 32),
      description: this.text(item.description, null),
    });
  }

  private createLanguageItemForm(item: ResumeLanguageItem): FormGroup<ResumeLanguageItemForm> {
    return new FormGroup<ResumeLanguageItemForm>({
      name: this.text(item.name, 255),
      proficiency: this.text(item.proficiency, 255),
    });
  }

  private createCertificationItemForm(
    item: ResumeCertificationItem,
  ): FormGroup<ResumeCertificationItemForm> {
    return new FormGroup<ResumeCertificationItemForm>({
      name: this.text(item.name, 255),
      issuer: this.text(item.issuer, 255),
      issuedOn: this.nullableText(item.issuedOn, 32),
      expiresOn: this.nullableText(item.expiresOn, 32),
      credentialUrl: this.text(item.credentialUrl, 512),
    });
  }

  private createAdditionalSectionForm(
    section: ResumeAdditionalSection,
  ): FormGroup<ResumeAdditionalSectionForm> {
    return new FormGroup<ResumeAdditionalSectionForm>({
      title: this.text(section.title, 255),
      items: new FormArray<FormGroup<ResumeAdditionalSectionItemForm>>(
        section.items.map((item) => this.createAdditionalSectionItemForm(item)),
      ),
    });
  }

  private createAdditionalSectionItemForm(
    item: ResumeAdditionalSectionItem,
  ): FormGroup<ResumeAdditionalSectionItemForm> {
    return new FormGroup<ResumeAdditionalSectionItemForm>({
      title: this.text(item.title, 255),
      description: this.text(item.description, null),
      url: this.text(item.url, 512),
    });
  }

  private text(value: string, maxLength: number | null): TextControl {
    if (maxLength === null) return this.formBuilder.control(value);
    return this.formBuilder.control(value, { validators: Validators.maxLength(maxLength) });
  }

  private nullableText(value: string | null, maxLength: number | null): NullableTextControl {
    if (maxLength === null) return new FormControl<string | null>(value);
    return new FormControl<string | null>(value, { validators: Validators.maxLength(maxLength) });
  }

  private currentStatus(value: ResumeCurrentStatus): CurrentStatusControl {
    return this.formBuilder.control(value);
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
      items: textToLines(value.itemsText),
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
      highlights: textToLines(value.highlightsText),
      technologies: textToLines(value.technologiesText),
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
      highlights: textToLines(value.highlightsText),
      technologies: textToLines(value.technologiesText),
      url: cleanText(value.url),
    };
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

  private resolveResumeId(): number {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isInteger(id)) return 0;
    return id;
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

function textToLines(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}

function linesToText(values: string[]): string {
  return values.join('\n');
}

function isResumeLanguage(value: string): value is ResumeLanguage {
  return value === 'ru' || value === 'en';
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
