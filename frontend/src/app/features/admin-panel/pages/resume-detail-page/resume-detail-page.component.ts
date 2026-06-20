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
type NullableBooleanControl = FormControl<boolean | null>;

interface ResumeEditorTabDefinition {
  key: ResumeEditorTab;
  labelKey: string;
}

interface ResumeProfileForm {
  fullName: NullableTextControl;
  roleRu: NullableTextControl;
  roleEn: NullableTextControl;
  locationRu: NullableTextControl;
  locationEn: NullableTextControl;
  email: NullableTextControl;
  phone: NullableTextControl;
  websiteUrl: NullableTextControl;
  linkedinUrl: NullableTextControl;
  githubUrl: NullableTextControl;
  telegram: NullableTextControl;
}

interface ResumeSummaryForm {
  textRu: NullableTextControl;
  textEn: NullableTextControl;
}

interface ResumeSkillGroupForm {
  categoryRu: NullableTextControl;
  categoryEn: NullableTextControl;
  itemsText: TextControl;
}

interface ResumeExperienceItemForm {
  companyRu: NullableTextControl;
  companyEn: NullableTextControl;
  positionRu: NullableTextControl;
  positionEn: NullableTextControl;
  locationRu: NullableTextControl;
  locationEn: NullableTextControl;
  startDate: NullableTextControl;
  endDate: NullableTextControl;
  isCurrent: NullableBooleanControl;
  summaryRu: NullableTextControl;
  summaryEn: NullableTextControl;
  highlightsRuText: TextControl;
  highlightsEnText: TextControl;
  technologiesText: TextControl;
  projects: FormArray<FormGroup<ResumeProjectItemForm>>;
}

interface ResumeProjectItemForm {
  nameRu: NullableTextControl;
  nameEn: NullableTextControl;
  roleRu: NullableTextControl;
  roleEn: NullableTextControl;
  descriptionRu: NullableTextControl;
  descriptionEn: NullableTextControl;
  highlightsRuText: TextControl;
  highlightsEnText: TextControl;
  technologiesText: TextControl;
  url: NullableTextControl;
}

interface ResumeEducationItemForm {
  institutionRu: NullableTextControl;
  institutionEn: NullableTextControl;
  degreeRu: NullableTextControl;
  degreeEn: NullableTextControl;
  fieldRu: NullableTextControl;
  fieldEn: NullableTextControl;
  locationRu: NullableTextControl;
  locationEn: NullableTextControl;
  startDate: NullableTextControl;
  endDate: NullableTextControl;
  descriptionRu: NullableTextControl;
  descriptionEn: NullableTextControl;
}

interface ResumeLanguageItemForm {
  nameRu: NullableTextControl;
  nameEn: NullableTextControl;
  proficiencyRu: NullableTextControl;
  proficiencyEn: NullableTextControl;
}

interface ResumeCertificationItemForm {
  nameRu: NullableTextControl;
  nameEn: NullableTextControl;
  issuerRu: NullableTextControl;
  issuerEn: NullableTextControl;
  issuedOn: NullableTextControl;
  expiresOn: NullableTextControl;
  credentialUrl: NullableTextControl;
}

interface ResumeAdditionalSectionItemForm {
  titleRu: NullableTextControl;
  titleEn: NullableTextControl;
  descriptionRu: NullableTextControl;
  descriptionEn: NullableTextControl;
  url: NullableTextControl;
}

interface ResumeAdditionalSectionForm {
  titleRu: NullableTextControl;
  titleEn: NullableTextControl;
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

  localized(ru: string | null, en: string | null): string | null {
    if (this.previewLanguage() === 'ru') return cleanNullableString(ru);
    return cleanNullableString(en);
  }

  dateRange(startDate: string | null, endDate: string | null, isCurrent: boolean | null): string {
    const start = cleanNullableString(startDate);
    const end = isCurrent
      ? this.i18n.translate('adminResumeWorkspace.field.isCurrent')
      : cleanNullableString(endDate);
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
      fullName: this.nullableText(profile.fullName, 255),
      roleRu: this.nullableText(profile.roleRu, 255),
      roleEn: this.nullableText(profile.roleEn, 255),
      locationRu: this.nullableText(profile.locationRu, 255),
      locationEn: this.nullableText(profile.locationEn, 255),
      email: this.nullableText(profile.email, 255),
      phone: this.nullableText(profile.phone, 255),
      websiteUrl: this.nullableText(profile.websiteUrl, 512),
      linkedinUrl: this.nullableText(profile.linkedinUrl, 512),
      githubUrl: this.nullableText(profile.githubUrl, 512),
      telegram: this.nullableText(profile.telegram, 255),
    });
  }

  private createSummaryForm(summary: ResumeSummary): FormGroup<ResumeSummaryForm> {
    return new FormGroup<ResumeSummaryForm>({
      textRu: this.nullableText(summary.textRu, null),
      textEn: this.nullableText(summary.textEn, null),
    });
  }

  private createSkillGroupForm(skill: ResumeSkillGroup): FormGroup<ResumeSkillGroupForm> {
    return new FormGroup<ResumeSkillGroupForm>({
      categoryRu: this.nullableText(skill.categoryRu, 255),
      categoryEn: this.nullableText(skill.categoryEn, 255),
      itemsText: this.text(linesToText(skill.items), null),
    });
  }

  private createExperienceItemForm(
    item: ResumeExperienceItem,
  ): FormGroup<ResumeExperienceItemForm> {
    return new FormGroup<ResumeExperienceItemForm>({
      companyRu: this.nullableText(item.companyRu, 255),
      companyEn: this.nullableText(item.companyEn, 255),
      positionRu: this.nullableText(item.positionRu, 255),
      positionEn: this.nullableText(item.positionEn, 255),
      locationRu: this.nullableText(item.locationRu, 255),
      locationEn: this.nullableText(item.locationEn, 255),
      startDate: this.nullableText(item.startDate, 32),
      endDate: this.nullableText(item.endDate, 32),
      isCurrent: this.nullableBoolean(item.isCurrent),
      summaryRu: this.nullableText(item.summaryRu, null),
      summaryEn: this.nullableText(item.summaryEn, null),
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
      nameRu: this.nullableText(item.nameRu, 255),
      nameEn: this.nullableText(item.nameEn, 255),
      roleRu: this.nullableText(item.roleRu, 255),
      roleEn: this.nullableText(item.roleEn, 255),
      descriptionRu: this.nullableText(item.descriptionRu, null),
      descriptionEn: this.nullableText(item.descriptionEn, null),
      highlightsRuText: this.text(linesToText(item.highlightsRu), null),
      highlightsEnText: this.text(linesToText(item.highlightsEn), null),
      technologiesText: this.text(linesToText(item.technologies), null),
      url: this.nullableText(item.url, 512),
    });
  }

  private createEducationItemForm(item: ResumeEducationItem): FormGroup<ResumeEducationItemForm> {
    return new FormGroup<ResumeEducationItemForm>({
      institutionRu: this.nullableText(item.institutionRu, 255),
      institutionEn: this.nullableText(item.institutionEn, 255),
      degreeRu: this.nullableText(item.degreeRu, 255),
      degreeEn: this.nullableText(item.degreeEn, 255),
      fieldRu: this.nullableText(item.fieldRu, 255),
      fieldEn: this.nullableText(item.fieldEn, 255),
      locationRu: this.nullableText(item.locationRu, 255),
      locationEn: this.nullableText(item.locationEn, 255),
      startDate: this.nullableText(item.startDate, 32),
      endDate: this.nullableText(item.endDate, 32),
      descriptionRu: this.nullableText(item.descriptionRu, null),
      descriptionEn: this.nullableText(item.descriptionEn, null),
    });
  }

  private createLanguageItemForm(item: ResumeLanguageItem): FormGroup<ResumeLanguageItemForm> {
    return new FormGroup<ResumeLanguageItemForm>({
      nameRu: this.nullableText(item.nameRu, 255),
      nameEn: this.nullableText(item.nameEn, 255),
      proficiencyRu: this.nullableText(item.proficiencyRu, 255),
      proficiencyEn: this.nullableText(item.proficiencyEn, 255),
    });
  }

  private createCertificationItemForm(
    item: ResumeCertificationItem,
  ): FormGroup<ResumeCertificationItemForm> {
    return new FormGroup<ResumeCertificationItemForm>({
      nameRu: this.nullableText(item.nameRu, 255),
      nameEn: this.nullableText(item.nameEn, 255),
      issuerRu: this.nullableText(item.issuerRu, 255),
      issuerEn: this.nullableText(item.issuerEn, 255),
      issuedOn: this.nullableText(item.issuedOn, 32),
      expiresOn: this.nullableText(item.expiresOn, 32),
      credentialUrl: this.nullableText(item.credentialUrl, 512),
    });
  }

  private createAdditionalSectionForm(
    section: ResumeAdditionalSection,
  ): FormGroup<ResumeAdditionalSectionForm> {
    return new FormGroup<ResumeAdditionalSectionForm>({
      titleRu: this.nullableText(section.titleRu, 255),
      titleEn: this.nullableText(section.titleEn, 255),
      items: new FormArray<FormGroup<ResumeAdditionalSectionItemForm>>(
        section.items.map((item) => this.createAdditionalSectionItemForm(item)),
      ),
    });
  }

  private createAdditionalSectionItemForm(
    item: ResumeAdditionalSectionItem,
  ): FormGroup<ResumeAdditionalSectionItemForm> {
    return new FormGroup<ResumeAdditionalSectionItemForm>({
      titleRu: this.nullableText(item.titleRu, 255),
      titleEn: this.nullableText(item.titleEn, 255),
      descriptionRu: this.nullableText(item.descriptionRu, null),
      descriptionEn: this.nullableText(item.descriptionEn, null),
      url: this.nullableText(item.url, 512),
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

  private nullableBoolean(value: boolean | null): NullableBooleanControl {
    return new FormControl<boolean | null>(value);
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
      fullName: cleanNullableString(value.fullName),
      roleRu: cleanNullableString(value.roleRu),
      roleEn: cleanNullableString(value.roleEn),
      locationRu: cleanNullableString(value.locationRu),
      locationEn: cleanNullableString(value.locationEn),
      email: cleanNullableString(value.email),
      phone: cleanNullableString(value.phone),
      websiteUrl: cleanNullableString(value.websiteUrl),
      linkedinUrl: cleanNullableString(value.linkedinUrl),
      githubUrl: cleanNullableString(value.githubUrl),
      telegram: cleanNullableString(value.telegram),
    };
  }

  private buildSummary(): ResumeSummary {
    const value = this.resumeForm.controls.summary.getRawValue();
    return {
      textRu: cleanNullableString(value.textRu),
      textEn: cleanNullableString(value.textEn),
    };
  }

  private buildSkillGroup(control: FormGroup<ResumeSkillGroupForm>): ResumeSkillGroup {
    const value = control.getRawValue();
    return {
      categoryRu: cleanNullableString(value.categoryRu),
      categoryEn: cleanNullableString(value.categoryEn),
      items: textToLines(value.itemsText),
    };
  }

  private buildExperienceItem(control: FormGroup<ResumeExperienceItemForm>): ResumeExperienceItem {
    const value = control.getRawValue();
    return {
      companyRu: cleanNullableString(value.companyRu),
      companyEn: cleanNullableString(value.companyEn),
      positionRu: cleanNullableString(value.positionRu),
      positionEn: cleanNullableString(value.positionEn),
      locationRu: cleanNullableString(value.locationRu),
      locationEn: cleanNullableString(value.locationEn),
      startDate: cleanNullableString(value.startDate),
      endDate: cleanNullableString(value.endDate),
      isCurrent: value.isCurrent,
      summaryRu: cleanNullableString(value.summaryRu),
      summaryEn: cleanNullableString(value.summaryEn),
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
      nameRu: cleanNullableString(value.nameRu),
      nameEn: cleanNullableString(value.nameEn),
      roleRu: cleanNullableString(value.roleRu),
      roleEn: cleanNullableString(value.roleEn),
      descriptionRu: cleanNullableString(value.descriptionRu),
      descriptionEn: cleanNullableString(value.descriptionEn),
      highlightsRu: textToLines(value.highlightsRuText),
      highlightsEn: textToLines(value.highlightsEnText),
      technologies: textToLines(value.technologiesText),
      url: cleanNullableString(value.url),
    };
  }

  private buildEducationItem(control: FormGroup<ResumeEducationItemForm>): ResumeEducationItem {
    const value = control.getRawValue();
    return {
      institutionRu: cleanNullableString(value.institutionRu),
      institutionEn: cleanNullableString(value.institutionEn),
      degreeRu: cleanNullableString(value.degreeRu),
      degreeEn: cleanNullableString(value.degreeEn),
      fieldRu: cleanNullableString(value.fieldRu),
      fieldEn: cleanNullableString(value.fieldEn),
      locationRu: cleanNullableString(value.locationRu),
      locationEn: cleanNullableString(value.locationEn),
      startDate: cleanNullableString(value.startDate),
      endDate: cleanNullableString(value.endDate),
      descriptionRu: cleanNullableString(value.descriptionRu),
      descriptionEn: cleanNullableString(value.descriptionEn),
    };
  }

  private buildLanguageItem(control: FormGroup<ResumeLanguageItemForm>): ResumeLanguageItem {
    const value = control.getRawValue();
    return {
      nameRu: cleanNullableString(value.nameRu),
      nameEn: cleanNullableString(value.nameEn),
      proficiencyRu: cleanNullableString(value.proficiencyRu),
      proficiencyEn: cleanNullableString(value.proficiencyEn),
    };
  }

  private buildCertificationItem(
    control: FormGroup<ResumeCertificationItemForm>,
  ): ResumeCertificationItem {
    const value = control.getRawValue();
    return {
      nameRu: cleanNullableString(value.nameRu),
      nameEn: cleanNullableString(value.nameEn),
      issuerRu: cleanNullableString(value.issuerRu),
      issuerEn: cleanNullableString(value.issuerEn),
      issuedOn: cleanNullableString(value.issuedOn),
      expiresOn: cleanNullableString(value.expiresOn),
      credentialUrl: cleanNullableString(value.credentialUrl),
    };
  }

  private buildAdditionalSection(
    control: FormGroup<ResumeAdditionalSectionForm>,
  ): ResumeAdditionalSection {
    const value = control.getRawValue();
    return {
      titleRu: cleanNullableString(value.titleRu),
      titleEn: cleanNullableString(value.titleEn),
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
      titleRu: cleanNullableString(value.titleRu),
      titleEn: cleanNullableString(value.titleEn),
      descriptionRu: cleanNullableString(value.descriptionRu),
      descriptionEn: cleanNullableString(value.descriptionEn),
      url: cleanNullableString(value.url),
    };
  }

  private resolveResumeId(): number {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isInteger(id)) return 0;
    return id;
  }
}

function cleanNullableString(value: string | null): string | null {
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
    fullName: null,
    roleRu: null,
    roleEn: null,
    locationRu: null,
    locationEn: null,
    email: null,
    phone: null,
    websiteUrl: null,
    linkedinUrl: null,
    githubUrl: null,
    telegram: null,
  };
}

function createEmptyResumeSummary(): ResumeSummary {
  return {
    textRu: null,
    textEn: null,
  };
}

function createEmptyResumeSkillGroup(): ResumeSkillGroup {
  return {
    categoryRu: null,
    categoryEn: null,
    items: [],
  };
}

function createEmptyResumeExperienceItem(): ResumeExperienceItem {
  return {
    companyRu: null,
    companyEn: null,
    positionRu: null,
    positionEn: null,
    locationRu: null,
    locationEn: null,
    startDate: null,
    endDate: null,
    isCurrent: null,
    summaryRu: null,
    summaryEn: null,
    highlightsRu: [],
    highlightsEn: [],
    technologies: [],
    projects: [],
  };
}

function createEmptyResumeProjectItem(): ResumeProjectItem {
  return {
    nameRu: null,
    nameEn: null,
    roleRu: null,
    roleEn: null,
    descriptionRu: null,
    descriptionEn: null,
    highlightsRu: [],
    highlightsEn: [],
    technologies: [],
    url: null,
  };
}

function createEmptyResumeEducationItem(): ResumeEducationItem {
  return {
    institutionRu: null,
    institutionEn: null,
    degreeRu: null,
    degreeEn: null,
    fieldRu: null,
    fieldEn: null,
    locationRu: null,
    locationEn: null,
    startDate: null,
    endDate: null,
    descriptionRu: null,
    descriptionEn: null,
  };
}

function createEmptyResumeLanguageItem(): ResumeLanguageItem {
  return {
    nameRu: null,
    nameEn: null,
    proficiencyRu: null,
    proficiencyEn: null,
  };
}

function createEmptyResumeCertificationItem(): ResumeCertificationItem {
  return {
    nameRu: null,
    nameEn: null,
    issuerRu: null,
    issuerEn: null,
    issuedOn: null,
    expiresOn: null,
    credentialUrl: null,
  };
}

function createEmptyResumeAdditionalSection(): ResumeAdditionalSection {
  return {
    titleRu: null,
    titleEn: null,
    items: [],
  };
}

function createEmptyResumeAdditionalSectionItem(): ResumeAdditionalSectionItem {
  return {
    titleRu: null,
    titleEn: null,
    descriptionRu: null,
    descriptionEn: null,
    url: null,
  };
}
