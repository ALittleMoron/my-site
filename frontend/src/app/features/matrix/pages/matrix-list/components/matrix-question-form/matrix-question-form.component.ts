import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  computed,
  inject,
  input,
  output,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { I18nService } from '../../../../../../core/i18n/i18n.service';
import { LanguageCode } from '../../../../../../core/i18n/i18n.model';
import {
  WikiLinkTargetLookup,
  findMissingWikiLinkTargets,
} from '../../../../../../core/wiki-links/wiki-links';
import { WikiLinkTargetsService } from '../../../../../../core/wiki-links/wiki-link-targets.service';
import {
  MatrixGrade,
  MatrixQuestionDetail,
  MatrixQuestionPayload,
  MatrixResource,
} from '../../../../models/matrix-question.model';
import {
  MatrixResourceDraft,
  MatrixResourcePickerComponent,
  toNewResourceTranslations,
} from '../matrix-resource-picker/matrix-resource-picker.component';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';

interface MatrixQuestionForm {
  slug: FormControl<string>;
  questionRu: FormControl<string>;
  questionEn: FormControl<string>;
  answerRu: FormControl<string>;
  answerEn: FormControl<string>;
  interviewExpectedAnswerRu: FormControl<string>;
  interviewExpectedAnswerEn: FormControl<string>;
  sheetKey: FormControl<string>;
  sheetRu: FormControl<string>;
  sheetEn: FormControl<string>;
  grade: FormControl<MatrixGrade>;
  sectionRu: FormControl<string>;
  sectionEn: FormControl<string>;
  subsectionRu: FormControl<string>;
  subsectionEn: FormControl<string>;
  publishStatus: FormControl<'Draft' | 'Published'>;
}

@Component({
  selector: 'app-matrix-question-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MarkdownEditorComponent,
    MatrixResourcePickerComponent,
    TranslatePipe,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-question-form.component.html',
})
export class MatrixQuestionFormComponent implements OnInit {
  private readonly wikiLinkTargetsService = inject(WikiLinkTargetsService);
  private readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);
  private slugEdited = false;

  readonly searchResults = input<MatrixResource[]>([]);
  readonly questionSave = output<MatrixQuestionPayload>();
  readonly formCancel = output<void>();
  readonly resourceSearch = output<string>();

  readonly resources = signal<MatrixResourceDraft[]>([]);
  readonly activeLanguageTab = signal<LanguageCode>('ru');
  readonly availableWikiLinkTargets = signal<WikiLinkTargetLookup | null>(null);

  readonly form = new FormGroup<MatrixQuestionForm>({
    slug: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.maxLength(255)],
    }),
    questionRu: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    questionEn: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    answerRu: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    answerEn: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    interviewExpectedAnswerRu: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required],
    }),
    interviewExpectedAnswerEn: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required],
    }),
    sheetKey: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    sheetRu: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    sheetEn: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    grade: new FormControl<MatrixGrade>('Junior', {
      nonNullable: true,
      validators: [Validators.required],
    }),
    sectionRu: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    sectionEn: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    subsectionRu: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    subsectionEn: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    publishStatus: new FormControl<'Draft' | 'Published'>('Draft', { nonNullable: true }),
  });

  readonly question = input<MatrixQuestionDetail | null>(null);
  readonly formSnapshot = signal(this.form.getRawValue());
  readonly activeMissingWikiLinkTargets = computed(() => {
    const value = this.formSnapshot();
    const language = this.activeLanguageTab();
    const markdown =
      language === 'ru'
        ? `${value.answerRu}\n${value.interviewExpectedAnswerRu}`
        : `${value.answerEn}\n${value.interviewExpectedAnswerEn}`;
    return missingWikiLinkTargets({
      markdown,
      availableTargets: this.availableWikiLinkTargets(),
    });
  });
  readonly hasMissingWikiLinkTargets = computed(
    () => this.activeMissingWikiLinkTargets().length > 0,
  );
  readonly missingWikiLinkTargetsText = computed(() =>
    this.activeMissingWikiLinkTargets().join(', '),
  );

  ngOnInit(): void {
    const question = this.question();
    if (question) {
      this.slugEdited = true;
      this.form.setValue({
        slug: question.slug,
        questionRu: question.translations.ru.question,
        questionEn: question.translations.en.question,
        answerRu: question.translations.ru.answer,
        answerEn: question.translations.en.answer,
        interviewExpectedAnswerRu: question.translations.ru.interviewExpectedAnswer,
        interviewExpectedAnswerEn: question.translations.en.interviewExpectedAnswer,
        sheetKey: question.sheetKey,
        sheetRu: question.translations.ru.sheet,
        sheetEn: question.translations.en.sheet,
        grade: question.grade ?? 'Junior',
        sectionRu: question.translations.ru.section,
        sectionEn: question.translations.en.section,
        subsectionRu: question.translations.ru.subsection,
        subsectionEn: question.translations.en.subsection,
        publishStatus: question.publishStatus,
      });
      this.formSnapshot.set(this.form.getRawValue());
      this.resources.set(
        question.resources.map(MatrixResourcePickerComponent.fromAttachedResource),
      );
    }
    this.form.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => {
      this.formSnapshot.set(this.form.getRawValue());
    });
    this.loadWikiLinkTargets();
  }

  setActiveLanguageTab(language: LanguageCode): void {
    this.activeLanguageTab.set(language);
  }

  onQuestionEnInput(): void {
    if (this.slugEdited) return;
    this.form.controls.slug.setValue(slugify(this.form.controls.questionEn.value));
  }

  onSlugInput(): void {
    this.slugEdited = true;
  }

  setAnswerRu(value: string): void {
    this.form.controls.answerRu.setValue(value);
  }

  setAnswerEn(value: string): void {
    this.form.controls.answerEn.setValue(value);
  }

  setInterviewExpectedAnswerRu(value: string): void {
    this.form.controls.interviewExpectedAnswerRu.setValue(value);
  }

  setInterviewExpectedAnswerEn(value: string): void {
    this.form.controls.interviewExpectedAnswerEn.setValue(value);
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.questionSave.emit({
      slug: value.slug,
      sheetKey: value.sheetKey,
      grade: value.grade,
      publishStatus: value.publishStatus,
      translations: {
        ru: {
          question: value.questionRu,
          answer: value.answerRu,
          interviewExpectedAnswer: value.interviewExpectedAnswerRu,
          sheet: value.sheetRu,
          section: value.sectionRu,
          subsection: value.subsectionRu,
        },
        en: {
          question: value.questionEn,
          answer: value.answerEn,
          interviewExpectedAnswer: value.interviewExpectedAnswerEn,
          sheet: value.sheetEn,
          section: value.sectionEn,
          subsection: value.subsectionEn,
        },
      },
      resources: this.resources().map((resource) =>
        resource.isNew
          ? {
              resource: {
                url: resource.url,
                translations: toNewResourceTranslations(resource.translations),
              },
              translations: {
                ru: { context: resource.translations.ru.context },
                en: { context: resource.translations.en.context },
              },
            }
          : {
              resourceId: resource.id,
              translations: {
                ru: { context: resource.translations.ru.context },
                en: { context: resource.translations.en.context },
              },
            },
      ),
    });
  }

  private loadWikiLinkTargets(): void {
    this.wikiLinkTargetsService
      .getTargets(this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (targets) => this.availableWikiLinkTargets.set(targets),
        error: () => this.availableWikiLinkTargets.set(null),
      });
  }

  private currentLanguage(): LanguageCode {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }
}

function missingWikiLinkTargets(params: {
  markdown: string;
  availableTargets: WikiLinkTargetLookup | null;
}): string[] {
  if (params.availableTargets === null) return [];
  return findMissingWikiLinkTargets({
    markdown: params.markdown,
    availableTargets: params.availableTargets,
  });
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
