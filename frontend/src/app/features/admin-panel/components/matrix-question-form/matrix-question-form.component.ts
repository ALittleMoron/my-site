import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  EventEmitter,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
  inject,
  signal,
} from '@angular/core';
import {
  AbstractControl,
  FormControl,
  NonNullableFormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { slugify } from '../../../../shared/utils/slugify';
import {
  AdminMatrixGrade,
  AdminMatrixInterviewFrequency,
  AdminMatrixMissingField,
  AdminMatrixQuestionDetailDto,
  AdminMatrixQuestionPayload,
  AdminMatrixResource,
  AdminMatrixResourceAttachmentPayload,
  AdminMatrixPublishStatus,
  missingMatrixQuestionPayloadFields,
} from '../../models/matrix-question-workspace.model';
import { MatrixQuestionWorkspaceService } from '../../services/matrix-question-workspace.service';
import { MatrixStructurePickerComponent } from '../matrix-structure-picker/matrix-structure-picker.component';

const GRADES: readonly AdminMatrixGrade[] = ['Junior', 'Junior+', 'Middle', 'Middle+', 'Senior'];
const INTERVIEW_FREQUENCIES: readonly AdminMatrixInterviewFrequency[] = [
  'constantly',
  'often',
  'rarely',
  'neverSeen',
];
const PUBLISH_STATUSES: readonly AdminMatrixPublishStatus[] = ['Draft', 'Published'];
const RESOURCE_SEARCH_LIMIT = 10;

type RequiredFormField = 'slug' | 'subsectionId' | 'questionRu' | 'questionEn';

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
  selector: 'app-admin-matrix-question-form',
  standalone: true,
  imports: [ReactiveFormsModule, TranslatePipe, MatrixStructurePickerComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-question-form.component.html',
  styles: [
    `
      .required-marker {
        color: var(--bs-danger);
        font-weight: 700;
      }
    `,
  ],
})
export class MatrixQuestionFormComponent implements OnChanges {
  private readonly workspaceService = inject(MatrixQuestionWorkspaceService);
  private readonly i18n = inject(I18nService);
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);

  @Input({ required: true }) mode!: 'create' | 'edit';
  @Input({ required: true }) question!: AdminMatrixQuestionDetailDto | null;
  @Input({ required: true }) submitting!: boolean;

  @Output() readonly questionSave = new EventEmitter<AdminMatrixQuestionPayload>();
  @Output() readonly formCancel = new EventEmitter<void>();

  readonly grades = GRADES;
  readonly interviewFrequencies = INTERVIEW_FREQUENCIES;
  readonly publishStatuses = PUBLISH_STATUSES;
  readonly formSubmitted = signal(false);
  readonly publishError = signal<string | null>(null);
  readonly resourceDrafts = signal<AdminMatrixResourceDraft[]>([]);
  readonly resourceSearchResults = signal<AdminMatrixResource[]>([]);
  readonly newResourceNameRu = signal('');
  readonly newResourceNameEn = signal('');
  readonly newResourceUrl = signal('');

  private nextNewResourceId = -1;

  readonly questionForm = this.formBuilder.group({
    slug: ['', [trimRequired, Validators.maxLength(255)]],
    subsectionId: new FormControl<number | null>(null, { validators: Validators.required }),
    grade: this.formBuilder.control<AdminMatrixGrade | ''>(''),
    interviewFrequency: this.formBuilder.control<AdminMatrixInterviewFrequency | ''>(''),
    publishStatus: this.formBuilder.control<AdminMatrixPublishStatus>('Draft', {
      validators: Validators.required,
    }),
    questionRu: ['', [trimRequired, Validators.maxLength(255)]],
    questionEn: ['', [trimRequired, Validators.maxLength(255)]],
    answerRu: [''],
    answerEn: [''],
    expectedAnswerRu: [''],
    expectedAnswerEn: [''],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['question'] || changes['mode']) {
      this.resetFromQuestion();
    }
  }

  submit(): void {
    this.formSubmitted.set(true);
    this.publishError.set(null);
    if (this.questionForm.invalid) {
      this.questionForm.markAllAsTouched();
      return;
    }
    const payload = this.buildQuestionPayload();
    const missingFields = missingMatrixQuestionPayloadFields(payload);
    if (payload.publishStatus === 'Published' && missingFields.length > 0) {
      this.publishError.set(
        this.i18n.translate('adminMatrixWorkspace.publishMissingFields', {
          fields: this.missingFieldsText(missingFields),
        }),
      );
      return;
    }
    this.questionSave.emit(payload);
  }

  fieldInvalid(field: RequiredFormField): boolean {
    const control = this.questionForm.controls[field];
    return control.invalid && (this.formSubmitted() || control.touched);
  }

  selectQuestionSubsection(subsectionId: number | null): void {
    this.questionForm.controls.subsectionId.setValue(subsectionId);
    this.questionForm.controls.subsectionId.markAsTouched();
    this.questionForm.controls.subsectionId.markAsDirty();
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
          this.publishError.set(this.i18n.translate('matrix.notify.resourcesError'));
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

  publishStatusLabel(status: AdminMatrixPublishStatus): string {
    return this.i18n.translate(`enum.publishStatus.${status}`);
  }

  missingFieldLabel(field: string): string {
    return this.i18n.translate(`adminMatrixWorkspace.missing.${field}`);
  }

  missingFieldsText(fields: readonly AdminMatrixMissingField[]): string {
    return fields.map((field) => this.missingFieldLabel(field)).join(', ');
  }

  currentLanguage(): 'ru' | 'en' {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }

  private resetFromQuestion(): void {
    this.formSubmitted.set(false);
    this.publishError.set(null);
    if (this.question === null) {
      this.questionForm.reset({
        slug: '',
        subsectionId: null,
        grade: '',
        interviewFrequency: '',
        publishStatus: 'Draft',
        questionRu: '',
        questionEn: '',
        answerRu: '',
        answerEn: '',
        expectedAnswerRu: '',
        expectedAnswerEn: '',
      });
      this.resetResourceDrafts();
      return;
    }
    this.questionForm.reset({
      slug: this.question.slug,
      subsectionId: this.question.subsectionId,
      grade: this.question.grade ?? '',
      interviewFrequency: this.question.interviewFrequency ?? '',
      publishStatus: this.question.publishStatus,
      questionRu: this.question.translations.ru.question,
      questionEn: this.question.translations.en.question,
      answerRu: this.question.translations.ru.answer,
      answerEn: this.question.translations.en.answer,
      expectedAnswerRu: this.question.translations.ru.interviewExpectedAnswer,
      expectedAnswerEn: this.question.translations.en.interviewExpectedAnswer,
    });
    this.resourceDrafts.set(this.question.resources.map(toResourceDraft));
    this.resourceSearchResults.set([]);
  }

  private buildQuestionPayload(): AdminMatrixQuestionPayload {
    const raw = this.questionForm.getRawValue();
    if (raw.subsectionId === null) {
      throw new Error('Matrix question subsection is required');
    }
    return {
      slug: raw.slug.trim(),
      subsectionId: raw.subsectionId,
      grade: raw.grade === '' ? null : raw.grade,
      interviewFrequency: raw.interviewFrequency === '' ? null : raw.interviewFrequency,
      publishStatus: raw.publishStatus,
      translations: {
        ru: {
          question: raw.questionRu.trim(),
          answer: raw.answerRu,
          interviewExpectedAnswer: raw.expectedAnswerRu,
        },
        en: {
          question: raw.questionEn.trim(),
          answer: raw.answerEn,
          interviewExpectedAnswer: raw.expectedAnswerEn,
        },
      },
      resources: this.resourceDrafts().map(toResourceAttachmentPayload),
    };
  }

  private resetResourceDrafts(): void {
    this.resourceDrafts.set([]);
    this.resourceSearchResults.set([]);
    this.newResourceNameRu.set('');
    this.newResourceNameEn.set('');
    this.newResourceUrl.set('');
    this.nextNewResourceId = -1;
  }
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
