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
import { ApiError } from '../../../../core/models/api-error.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
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
type ResumePreviewLanguage = 'ru' | 'en';
type TextControl = FormControl<string>;
type NullableTextControl = FormControl<string | null>;
type CurrentStatusControl = FormControl<ResumeCurrentStatus>;

interface ResumeEditorTabDefinition {
  key: ResumeEditorTab;
  labelKey: string;
}

interface ResumeCurrentStatusOption {
  value: ResumeCurrentStatus;
  labelKey: string;
}

interface ResumeProfileForm {
  fullName: TextControl;
  roleRu: TextControl;
  roleEn: TextControl;
  locationRu: TextControl;
  locationEn: TextControl;
  email: TextControl;
  phone: TextControl;
  websiteUrl: TextControl;
  linkedinUrl: TextControl;
  githubUrl: TextControl;
  telegram: TextControl;
}

interface ResumeSummaryForm {
  textRu: TextControl;
  textEn: TextControl;
}

interface ResumeSkillGroupForm {
  categoryRu: TextControl;
  categoryEn: TextControl;
  itemsText: TextControl;
}

interface ResumeExperienceItemForm {
  companyRu: TextControl;
  companyEn: TextControl;
  positionRu: TextControl;
  positionEn: TextControl;
  locationRu: TextControl;
  locationEn: TextControl;
  startDate: NullableTextControl;
  endDate: NullableTextControl;
  currentStatus: CurrentStatusControl;
  summaryRu: TextControl;
  summaryEn: TextControl;
  highlightsRuText: TextControl;
  highlightsEnText: TextControl;
  technologiesText: TextControl;
  projects: FormArray<FormGroup<ResumeProjectItemForm>>;
}

interface ResumeProjectItemForm {
  nameRu: TextControl;
  nameEn: TextControl;
  roleRu: TextControl;
  roleEn: TextControl;
  descriptionRu: TextControl;
  descriptionEn: TextControl;
  highlightsRuText: TextControl;
  highlightsEnText: TextControl;
  technologiesText: TextControl;
  url: TextControl;
}

interface ResumeEducationItemForm {
  institutionRu: TextControl;
  institutionEn: TextControl;
  degreeRu: TextControl;
  degreeEn: TextControl;
  fieldRu: TextControl;
  fieldEn: TextControl;
  locationRu: TextControl;
  locationEn: TextControl;
  startDate: NullableTextControl;
  endDate: NullableTextControl;
  descriptionRu: TextControl;
  descriptionEn: TextControl;
}

interface ResumeLanguageItemForm {
  nameRu: TextControl;
  nameEn: TextControl;
  proficiencyRu: TextControl;
  proficiencyEn: TextControl;
}

interface ResumeCertificationItemForm {
  nameRu: TextControl;
  nameEn: TextControl;
  issuerRu: TextControl;
  issuerEn: TextControl;
  issuedOn: NullableTextControl;
  expiresOn: NullableTextControl;
  credentialUrl: TextControl;
}

interface ResumeAdditionalSectionItemForm {
  titleRu: TextControl;
  titleEn: TextControl;
  descriptionRu: TextControl;
  descriptionEn: TextControl;
  url: TextControl;
}

interface ResumeAdditionalSectionForm {
  titleRu: TextControl;
  titleEn: TextControl;
  items: FormArray<FormGroup<ResumeAdditionalSectionItemForm>>;
}

interface ResumeEditorForm {
  title: TextControl;
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
  readonly activeTab = signal<ResumeEditorTab>('profile');
  readonly mode = signal<ResumeEditorMode>('edit');
  readonly previewLanguage = computed<ResumePreviewLanguage>(() => this.currentLanguage());
  readonly dateLocale = computed(() => this.i18n.dateLocale());
  readonly datePlaceholder = computed(() => {
    this.currentLanguage();
    return this.i18n.translate('shared.datePicker.placeholder');
  });
  readonly openCalendarLabel = computed(() => {
    this.currentLanguage();
    return this.i18n.translate('shared.datePicker.open');
  });
  readonly previousMonthLabel = computed(() => {
    this.currentLanguage();
    return this.i18n.translate('shared.datePicker.previousMonth');
  });
  readonly nextMonthLabel = computed(() => {
    this.currentLanguage();
    return this.i18n.translate('shared.datePicker.nextMonth');
  });
  readonly openMonthYearPickerLabel = computed(() => {
    this.currentLanguage();
    return this.i18n.translate('shared.datePicker.openMonthYearPicker');
  });
  readonly previousYearLabel = computed(() => {
    this.currentLanguage();
    return this.i18n.translate('shared.datePicker.previousYear');
  });
  readonly nextYearLabel = computed(() => {
    this.currentLanguage();
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

  localized(ru: string, en: string): string | null {
    if (this.previewLanguage() === 'ru') return cleanPreviewText(ru);
    return cleanPreviewText(en);
  }

  dateRange(
    startDate: string | null,
    endDate: string | null,
    currentStatus: ResumeCurrentStatus,
  ): string {
    const start = cleanNullableDateString(startDate);
    const end =
      currentStatus === 'current'
        ? this.i18n.translate('adminResumeWorkspace.currentStatus.current')
        : cleanNullableDateString(endDate);
    return [start, end].filter(Boolean).join(' - ');
  }

  updateDate(control: NullableTextControl, value: string): void {
    control.setValue(value);
    control.markAsDirty();
    control.markAsTouched();
  }

  hasSummary(content: ResumeContent): boolean {
    return Boolean(this.localized(content.summary.textRu, content.summary.textEn));
  }

  buildPayload(): ResumePayload {
    const title = this.resumeForm.controls.title.getRawValue().trim();
    return {
      title,
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
      roleRu: this.text(profile.roleRu, 255),
      roleEn: this.text(profile.roleEn, 255),
      locationRu: this.text(profile.locationRu, 255),
      locationEn: this.text(profile.locationEn, 255),
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
      textRu: this.text(summary.textRu, null),
      textEn: this.text(summary.textEn, null),
    });
  }

  private createSkillGroupForm(skill: ResumeSkillGroup): FormGroup<ResumeSkillGroupForm> {
    return new FormGroup<ResumeSkillGroupForm>({
      categoryRu: this.text(skill.categoryRu, 255),
      categoryEn: this.text(skill.categoryEn, 255),
      itemsText: this.text(linesToText(skill.items), null),
    });
  }

  private createExperienceItemForm(
    item: ResumeExperienceItem,
  ): FormGroup<ResumeExperienceItemForm> {
    return new FormGroup<ResumeExperienceItemForm>({
      companyRu: this.text(item.companyRu, 255),
      companyEn: this.text(item.companyEn, 255),
      positionRu: this.text(item.positionRu, 255),
      positionEn: this.text(item.positionEn, 255),
      locationRu: this.text(item.locationRu, 255),
      locationEn: this.text(item.locationEn, 255),
      startDate: this.nullableText(item.startDate, 32),
      endDate: this.nullableText(item.endDate, 32),
      currentStatus: this.currentStatus(item.currentStatus),
      summaryRu: this.text(item.summaryRu, null),
      summaryEn: this.text(item.summaryEn, null),
      highlightsRuText: this.text(linesToText(item.highlightsRu), null),
      highlightsEnText: this.text(linesToText(item.highlightsEn), null),
      technologiesText: this.text(linesToText(item.technologies), null),
      projects: new FormArray<FormGroup<ResumeProjectItemForm>>(
        item.projects.map((project) => this.createProjectItemForm(project)),
      ),
    });
  }

  private createProjectItemForm(item: ResumeProjectItem): FormGroup<ResumeProjectItemForm> {
    return new FormGroup<ResumeProjectItemForm>({
      nameRu: this.text(item.nameRu, 255),
      nameEn: this.text(item.nameEn, 255),
      roleRu: this.text(item.roleRu, 255),
      roleEn: this.text(item.roleEn, 255),
      descriptionRu: this.text(item.descriptionRu, null),
      descriptionEn: this.text(item.descriptionEn, null),
      highlightsRuText: this.text(linesToText(item.highlightsRu), null),
      highlightsEnText: this.text(linesToText(item.highlightsEn), null),
      technologiesText: this.text(linesToText(item.technologies), null),
      url: this.text(item.url, 512),
    });
  }

  private createEducationItemForm(item: ResumeEducationItem): FormGroup<ResumeEducationItemForm> {
    return new FormGroup<ResumeEducationItemForm>({
      institutionRu: this.text(item.institutionRu, 255),
      institutionEn: this.text(item.institutionEn, 255),
      degreeRu: this.text(item.degreeRu, 255),
      degreeEn: this.text(item.degreeEn, 255),
      fieldRu: this.text(item.fieldRu, 255),
      fieldEn: this.text(item.fieldEn, 255),
      locationRu: this.text(item.locationRu, 255),
      locationEn: this.text(item.locationEn, 255),
      startDate: this.nullableText(item.startDate, 32),
      endDate: this.nullableText(item.endDate, 32),
      descriptionRu: this.text(item.descriptionRu, null),
      descriptionEn: this.text(item.descriptionEn, null),
    });
  }

  private createLanguageItemForm(item: ResumeLanguageItem): FormGroup<ResumeLanguageItemForm> {
    return new FormGroup<ResumeLanguageItemForm>({
      nameRu: this.text(item.nameRu, 255),
      nameEn: this.text(item.nameEn, 255),
      proficiencyRu: this.text(item.proficiencyRu, 255),
      proficiencyEn: this.text(item.proficiencyEn, 255),
    });
  }

  private createCertificationItemForm(
    item: ResumeCertificationItem,
  ): FormGroup<ResumeCertificationItemForm> {
    return new FormGroup<ResumeCertificationItemForm>({
      nameRu: this.text(item.nameRu, 255),
      nameEn: this.text(item.nameEn, 255),
      issuerRu: this.text(item.issuerRu, 255),
      issuerEn: this.text(item.issuerEn, 255),
      issuedOn: this.nullableText(item.issuedOn, 32),
      expiresOn: this.nullableText(item.expiresOn, 32),
      credentialUrl: this.text(item.credentialUrl, 512),
    });
  }

  private createAdditionalSectionForm(
    section: ResumeAdditionalSection,
  ): FormGroup<ResumeAdditionalSectionForm> {
    return new FormGroup<ResumeAdditionalSectionForm>({
      titleRu: this.text(section.titleRu, 255),
      titleEn: this.text(section.titleEn, 255),
      items: new FormArray<FormGroup<ResumeAdditionalSectionItemForm>>(
        section.items.map((item) => this.createAdditionalSectionItemForm(item)),
      ),
    });
  }

  private createAdditionalSectionItemForm(
    item: ResumeAdditionalSectionItem,
  ): FormGroup<ResumeAdditionalSectionItemForm> {
    return new FormGroup<ResumeAdditionalSectionItemForm>({
      titleRu: this.text(item.titleRu, 255),
      titleEn: this.text(item.titleEn, 255),
      descriptionRu: this.text(item.descriptionRu, null),
      descriptionEn: this.text(item.descriptionEn, null),
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

  private currentLanguage(): ResumePreviewLanguage {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }

  private buildProfile(): ResumeProfile {
    const value = this.resumeForm.controls.profile.getRawValue();
    return {
      fullName: cleanText(value.fullName),
      roleRu: cleanText(value.roleRu),
      roleEn: cleanText(value.roleEn),
      locationRu: cleanText(value.locationRu),
      locationEn: cleanText(value.locationEn),
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
      textRu: cleanText(value.textRu),
      textEn: cleanText(value.textEn),
    };
  }

  private buildSkillGroup(control: FormGroup<ResumeSkillGroupForm>): ResumeSkillGroup {
    const value = control.getRawValue();
    return {
      categoryRu: cleanText(value.categoryRu),
      categoryEn: cleanText(value.categoryEn),
      items: textToLines(value.itemsText),
    };
  }

  private buildExperienceItem(control: FormGroup<ResumeExperienceItemForm>): ResumeExperienceItem {
    const value = control.getRawValue();
    return {
      companyRu: cleanText(value.companyRu),
      companyEn: cleanText(value.companyEn),
      positionRu: cleanText(value.positionRu),
      positionEn: cleanText(value.positionEn),
      locationRu: cleanText(value.locationRu),
      locationEn: cleanText(value.locationEn),
      startDate: cleanNullableDateString(value.startDate),
      endDate: cleanNullableDateString(value.endDate),
      currentStatus: value.currentStatus,
      summaryRu: cleanText(value.summaryRu),
      summaryEn: cleanText(value.summaryEn),
      highlightsRu: textToLines(value.highlightsRuText),
      highlightsEn: textToLines(value.highlightsEnText),
      technologies: textToLines(value.technologiesText),
      projects: control.controls.projects.controls.map((projectControl) =>
        this.buildProjectItem(projectControl),
      ),
    };
  }

  private buildProjectItem(control: FormGroup<ResumeProjectItemForm>): ResumeProjectItem {
    const value = control.getRawValue();
    return {
      nameRu: cleanText(value.nameRu),
      nameEn: cleanText(value.nameEn),
      roleRu: cleanText(value.roleRu),
      roleEn: cleanText(value.roleEn),
      descriptionRu: cleanText(value.descriptionRu),
      descriptionEn: cleanText(value.descriptionEn),
      highlightsRu: textToLines(value.highlightsRuText),
      highlightsEn: textToLines(value.highlightsEnText),
      technologies: textToLines(value.technologiesText),
      url: cleanText(value.url),
    };
  }

  private buildEducationItem(control: FormGroup<ResumeEducationItemForm>): ResumeEducationItem {
    const value = control.getRawValue();
    return {
      institutionRu: cleanText(value.institutionRu),
      institutionEn: cleanText(value.institutionEn),
      degreeRu: cleanText(value.degreeRu),
      degreeEn: cleanText(value.degreeEn),
      fieldRu: cleanText(value.fieldRu),
      fieldEn: cleanText(value.fieldEn),
      locationRu: cleanText(value.locationRu),
      locationEn: cleanText(value.locationEn),
      startDate: cleanNullableDateString(value.startDate),
      endDate: cleanNullableDateString(value.endDate),
      descriptionRu: cleanText(value.descriptionRu),
      descriptionEn: cleanText(value.descriptionEn),
    };
  }

  private buildLanguageItem(control: FormGroup<ResumeLanguageItemForm>): ResumeLanguageItem {
    const value = control.getRawValue();
    return {
      nameRu: cleanText(value.nameRu),
      nameEn: cleanText(value.nameEn),
      proficiencyRu: cleanText(value.proficiencyRu),
      proficiencyEn: cleanText(value.proficiencyEn),
    };
  }

  private buildCertificationItem(
    control: FormGroup<ResumeCertificationItemForm>,
  ): ResumeCertificationItem {
    const value = control.getRawValue();
    return {
      nameRu: cleanText(value.nameRu),
      nameEn: cleanText(value.nameEn),
      issuerRu: cleanText(value.issuerRu),
      issuerEn: cleanText(value.issuerEn),
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
      titleRu: cleanText(value.titleRu),
      titleEn: cleanText(value.titleEn),
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
      titleRu: cleanText(value.titleRu),
      titleEn: cleanText(value.titleEn),
      descriptionRu: cleanText(value.descriptionRu),
      descriptionEn: cleanText(value.descriptionEn),
      url: cleanText(value.url),
    };
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
    roleRu: '',
    roleEn: '',
    locationRu: '',
    locationEn: '',
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
    textRu: '',
    textEn: '',
  };
}

function createEmptyResumeSkillGroup(): ResumeSkillGroup {
  return {
    categoryRu: '',
    categoryEn: '',
    items: [],
  };
}

function createEmptyResumeExperienceItem(): ResumeExperienceItem {
  return {
    companyRu: '',
    companyEn: '',
    positionRu: '',
    positionEn: '',
    locationRu: '',
    locationEn: '',
    startDate: null,
    endDate: null,
    currentStatus: 'notSet',
    summaryRu: '',
    summaryEn: '',
    highlightsRu: [],
    highlightsEn: [],
    technologies: [],
    projects: [],
  };
}

function createEmptyResumeProjectItem(): ResumeProjectItem {
  return {
    nameRu: '',
    nameEn: '',
    roleRu: '',
    roleEn: '',
    descriptionRu: '',
    descriptionEn: '',
    highlightsRu: [],
    highlightsEn: [],
    technologies: [],
    url: '',
  };
}

function createEmptyResumeEducationItem(): ResumeEducationItem {
  return {
    institutionRu: '',
    institutionEn: '',
    degreeRu: '',
    degreeEn: '',
    fieldRu: '',
    fieldEn: '',
    locationRu: '',
    locationEn: '',
    startDate: null,
    endDate: null,
    descriptionRu: '',
    descriptionEn: '',
  };
}

function createEmptyResumeLanguageItem(): ResumeLanguageItem {
  return {
    nameRu: '',
    nameEn: '',
    proficiencyRu: '',
    proficiencyEn: '',
  };
}

function createEmptyResumeCertificationItem(): ResumeCertificationItem {
  return {
    nameRu: '',
    nameEn: '',
    issuerRu: '',
    issuerEn: '',
    issuedOn: null,
    expiresOn: null,
    credentialUrl: '',
  };
}

function createEmptyResumeAdditionalSection(): ResumeAdditionalSection {
  return {
    titleRu: '',
    titleEn: '',
    items: [],
  };
}

function createEmptyResumeAdditionalSectionItem(): ResumeAdditionalSectionItem {
  return {
    titleRu: '',
    titleEn: '',
    descriptionRu: '',
    descriptionEn: '',
    url: '',
  };
}
