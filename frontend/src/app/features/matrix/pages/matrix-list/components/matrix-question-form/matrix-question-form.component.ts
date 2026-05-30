import { ChangeDetectionStrategy, Component, OnInit, input, output, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import {
  MatrixQuestionDetail,
  MatrixQuestionPayload,
  MatrixResource,
} from '../../../../models/matrix-question.model';
import {
  MatrixResourceDraft,
  MatrixResourcePickerComponent,
} from '../matrix-resource-picker/matrix-resource-picker.component';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';

interface MatrixQuestionForm {
  question: FormControl<string>;
  answer: FormControl<string>;
  interviewExpectedAnswer: FormControl<string>;
  sheet: FormControl<string>;
  grade: FormControl<string>;
  section: FormControl<string>;
  subsection: FormControl<string>;
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
  readonly searchResults = input<MatrixResource[]>([]);
  readonly questionSave = output<MatrixQuestionPayload>();
  readonly formCancel = output<void>();
  readonly resourceSearch = output<string>();

  readonly resources = signal<MatrixResourceDraft[]>([]);

  readonly form = new FormGroup<MatrixQuestionForm>({
    question: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    answer: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    interviewExpectedAnswer: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required],
    }),
    sheet: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    grade: new FormControl('Junior', { nonNullable: true, validators: [Validators.required] }),
    section: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    subsection: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    publishStatus: new FormControl<'Draft' | 'Published'>('Draft', { nonNullable: true }),
  });

  readonly question = input<MatrixQuestionDetail | null>(null);

  ngOnInit(): void {
    const question = this.question();
    if (!question) return;
    this.form.setValue({
      question: question.question,
      answer: question.answer,
      interviewExpectedAnswer: question.interviewExpectedAnswer,
      sheet: question.sheet,
      grade: question.grade ?? 'Junior',
      section: question.section,
      subsection: question.subsection,
      publishStatus: question.publishStatus,
    });
    this.resources.set(question.resources.map((resource) => ({ ...resource, isNew: false })));
  }

  setAnswer(value: string): void {
    this.form.controls.answer.setValue(value);
  }

  setInterviewExpectedAnswer(value: string): void {
    this.form.controls.interviewExpectedAnswer.setValue(value);
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.questionSave.emit({
      ...value,
      resources: this.resources().map((resource) =>
        resource.isNew
          ? { resource: { name: resource.name, url: resource.url }, context: resource.context }
          : { resourceId: resource.id, context: resource.context },
      ),
    });
  }
}
