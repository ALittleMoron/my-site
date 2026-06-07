import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { ReactiveFormsModule, Validators } from '@angular/forms';
import { NonNullableFormBuilder } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ApiError } from '../../../../core/models/api-error.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import {
  AdminMatrixGrade,
  AdminMatrixItemPayload,
  QueuedMatrixQuestion,
} from '../../models/matrix-question-queue.model';
import { MatrixQuestionQueueService } from '../../services/matrix-question-queue.service';

const GRADES: readonly AdminMatrixGrade[] = ['Junior', 'Junior+', 'Middle', 'Middle+', 'Senior'];

@Component({
  selector: 'app-matrix-question-queue-page',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    TranslatePipe,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-question-queue-page.component.html',
})
export class MatrixQuestionQueuePageComponent implements OnInit {
  private readonly queueService = inject(MatrixQuestionQueueService);
  private readonly notifications = inject(NotificationService);
  readonly i18n = inject(I18nService);
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);

  readonly grades = GRADES;
  readonly questions = signal<QueuedMatrixQuestion[]>([]);
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly selectedQuestion = signal<QueuedMatrixQuestion | null>(null);
  readonly submitting = signal(false);
  readonly rejectingQuestionId = signal<number | null>(null);
  readonly hasQuestions = computed(() => this.questions().length > 0);

  readonly form = this.formBuilder.group({
    slug: ['', [Validators.required, Validators.maxLength(255)]],
    sheetKey: ['', [Validators.required, Validators.maxLength(255)]],
    grade: this.formBuilder.control<AdminMatrixGrade>('Junior', {
      validators: Validators.required,
    }),
    questionRu: ['', [Validators.required, Validators.maxLength(255)]],
    questionEn: ['', [Validators.required, Validators.maxLength(255)]],
    answerRu: ['', Validators.required],
    answerEn: ['', Validators.required],
    expectedAnswerRu: ['', Validators.required],
    expectedAnswerEn: ['', Validators.required],
    sheetRu: ['', [Validators.required, Validators.maxLength(255)]],
    sheetEn: ['', [Validators.required, Validators.maxLength(255)]],
    sectionRu: ['', [Validators.required, Validators.maxLength(255)]],
    sectionEn: ['', [Validators.required, Validators.maxLength(255)]],
    subsectionRu: ['', [Validators.required, Validators.maxLength(255)]],
    subsectionEn: ['', [Validators.required, Validators.maxLength(255)]],
  });

  ngOnInit(): void {
    this.loadQueue();
  }

  loadQueue(): void {
    this.loading.set(true);
    this.error.set(null);
    this.queueService
      .listQueuedQuestions()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (questions) => {
          this.questions.set(questions);
          this.loading.set(false);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
          this.notifications.error(this.i18n.translate('adminMatrixQueue.loadError'));
        },
      });
  }

  selectQuestion(question: QueuedMatrixQuestion): void {
    this.selectedQuestion.set(question);
    const sheet = question.sheet ?? '';
    const section = question.section ?? '';
    const subsection = question.subsection ?? '';
    this.form.reset({
      slug: `queued-question-${question.id}`,
      sheetKey: sheet.toLowerCase().replaceAll(' ', '-'),
      grade: question.grade ?? 'Junior',
      questionRu: question.question,
      questionEn: question.question,
      answerRu: '',
      answerEn: '',
      expectedAnswerRu: '',
      expectedAnswerEn: '',
      sheetRu: sheet,
      sheetEn: sheet,
      sectionRu: section,
      sectionEn: section,
      subsectionRu: subsection,
      subsectionEn: subsection,
    });
  }

  rejectQuestion(question: QueuedMatrixQuestion): void {
    this.rejectingQuestionId.set(question.id);
    this.queueService
      .rejectQueuedQuestion(question.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.rejectingQuestionId.set(null);
          if (this.selectedQuestion()?.id === question.id) {
            this.selectedQuestion.set(null);
          }
          this.notifications.success(this.i18n.translate('adminMatrixQueue.rejected'));
          this.loadQueue();
        },
        error: () => {
          this.rejectingQuestionId.set(null);
          this.notifications.error(this.i18n.translate('adminMatrixQueue.rejectError'));
        },
      });
  }

  createQuestion(): void {
    const question = this.selectedQuestion();
    if (question === null || this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.submitting.set(true);
    this.queueService
      .createQuestionFromQueue(question.id, this.toPayload(), this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.submitting.set(false);
          this.selectedQuestion.set(null);
          this.notifications.success(this.i18n.translate('adminMatrixQueue.created'));
          this.loadQueue();
        },
        error: () => {
          this.submitting.set(false);
          this.notifications.error(this.i18n.translate('adminMatrixQueue.createError'));
        },
      });
  }

  questionStructure(question: QueuedMatrixQuestion): string {
    return [question.grade, question.sheet, question.section, question.subsection]
      .filter((value) => value !== null && value !== '')
      .join(' / ');
  }

  private toPayload(): AdminMatrixItemPayload {
    const value = this.form.getRawValue();
    return {
      slug: value.slug,
      sheetKey: value.sheetKey,
      grade: value.grade,
      publishStatus: 'Draft',
      translations: {
        ru: {
          question: value.questionRu,
          answer: value.answerRu,
          interviewExpectedAnswer: value.expectedAnswerRu,
          sheet: value.sheetRu,
          section: value.sectionRu,
          subsection: value.subsectionRu,
        },
        en: {
          question: value.questionEn,
          answer: value.answerEn,
          interviewExpectedAnswer: value.expectedAnswerEn,
          sheet: value.sheetEn,
          section: value.sectionEn,
          subsection: value.subsectionEn,
        },
      },
      resources: [],
    };
  }

  private currentLanguage(): 'ru' | 'en' {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }
}
