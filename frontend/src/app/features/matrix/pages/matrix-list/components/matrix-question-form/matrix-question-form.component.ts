import { ChangeDetectionStrategy, Component, OnInit, input, output, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { LanguageCode } from '../../../../../../core/i18n/i18n.model';
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
  private slugEdited = false;

  readonly searchResults = input<MatrixResource[]>([]);
  readonly questionSave = output<MatrixQuestionPayload>();
  readonly formCancel = output<void>();
  readonly resourceSearch = output<string>();

  readonly resources = signal<MatrixResourceDraft[]>([]);
  readonly activeLanguageTab = signal<LanguageCode>('ru');

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

  ngOnInit(): void {
    const question = this.question();
    if (!question) return;
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
    this.resources.set(question.resources.map(MatrixResourcePickerComponent.fromAttachedResource));
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
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
