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
import { ApiError } from '../../../../core/models/api-error.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import {
  ErrorMessageComponent,
  flattenNestedErrorMessages,
} from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { MatrixQuestionFormComponent } from '../../components/matrix-question-form/matrix-question-form.component';
import { QueuedMatrixQuestion } from '../../models/matrix-question-queue.model';
import {
  AdminMatrixQuestionCreateInitialValue,
  AdminMatrixQuestionPayload,
} from '../../models/matrix-question-workspace.model';
import { MatrixQuestionQueueService } from '../../services/matrix-question-queue.service';
import { ADMIN_VALIDATION_LIMITS } from '../../utils/admin-validation';

const LINE_BREAKS_PATTERN = /[\r\n]+/g;
const IMPORT_FILE_ACCEPT =
  '.txt,.csv,.xlsx,.xlsm,text/plain,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel.sheet.macroEnabled.12';

type QueueAddMode = 'manual' | 'import';

@Component({
  selector: 'app-matrix-question-queue-page',
  standalone: true,
  imports: [
    TranslatePipe,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
    MatrixQuestionFormComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-question-queue-page.component.html',
})
export class MatrixQuestionQueuePageComponent implements OnInit {
  private readonly queueService = inject(MatrixQuestionQueueService);
  private readonly notifications = inject(NotificationService);
  readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);

  readonly questions = signal<QueuedMatrixQuestion[]>([]);
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly selectedQuestion = signal<QueuedMatrixQuestion | null>(null);
  readonly submitting = signal(false);
  readonly formError = signal<ApiError | null>(null);
  readonly rejectingQuestionId = signal<string | null>(null);
  readonly manualAddVisible = signal(false);
  readonly addMode = signal<QueueAddMode>('manual');
  readonly manualAddQuestion = signal('');
  readonly manualAddSubmitted = signal(false);
  readonly manualAddSubmitting = signal(false);
  readonly importFileAccept = IMPORT_FILE_ACCEPT;
  readonly selectedImportFile = signal<File | null>(null);
  readonly importSubmitting = signal(false);
  readonly importError = signal<ApiError | null>(null);
  readonly importFileSelectionErrorKey = signal<string | null>(null);
  readonly hasQuestions = computed(() => this.questions().length > 0);
  readonly manualAddQuestionError = computed(() => {
    const question = this.manualAddQuestion().trim();
    if (question.length === 0) return 'validation.required';
    if (question.length > ADMIN_VALIDATION_LIMITS.shortText) return 'validation.maxLength';
    return null;
  });
  readonly selectedImportFileLabel = computed(() => {
    const file = this.selectedImportFile();
    if (file === null) return null;
    return this.i18n.translate('adminMatrixQueue.importSelectedFile', { filename: file.name });
  });
  readonly importNestedErrorMessages = computed(() => {
    const error = this.importError();
    if (error === null) return [];
    return flattenNestedErrorMessages(error);
  });
  readonly formErrorMessages = computed(() => {
    const error = this.formError();
    if (error === null) return [];
    const nestedMessages = flattenNestedErrorMessages(error);
    return nestedMessages.length > 0 ? nestedMessages : [error.message];
  });
  readonly selectedQuestionInitialValue = computed<AdminMatrixQuestionCreateInitialValue | null>(
    () => {
      const question = this.selectedQuestion();
      if (question === null) return null;
      return {
        slug: `queued-question-${question.id}`,
        subsectionId: null,
        preferredSheetKey: question.sheet,
        grade: question.grade,
        interviewFrequency: null,
        publishStatus: 'Draft',
        translations: {
          ru: {
            question: question.question,
            answer: '',
            interviewExpectedAnswer: '',
          },
          en: {
            question: question.question,
            answer: '',
            interviewExpectedAnswer: '',
          },
        },
      };
    },
  );

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
    this.formError.set(null);
    this.submitting.set(false);
  }

  closeCreateModal(): void {
    if (this.submitting()) return;
    this.selectedQuestion.set(null);
    this.formError.set(null);
  }

  openManualAdd(): void {
    this.manualAddVisible.set(true);
    this.addMode.set('manual');
    this.manualAddQuestion.set('');
    this.manualAddSubmitted.set(false);
    this.manualAddSubmitting.set(false);
    this.resetImportState();
  }

  closeManualAdd(): void {
    if (this.manualAddSubmitting() || this.importSubmitting()) return;
    this.manualAddVisible.set(false);
    this.manualAddQuestion.set('');
    this.manualAddSubmitted.set(false);
    this.addMode.set('manual');
    this.resetImportState();
  }

  setAddMode(mode: QueueAddMode): void {
    this.addMode.set(mode);
    this.importError.set(null);
    this.importFileSelectionErrorKey.set(null);
  }

  setManualAddQuestion(value: string): void {
    this.manualAddQuestion.set(normalizeManualQuestion(value));
  }

  onManualAddQuestionInput(event: Event): void {
    const target = event.target as HTMLInputElement | null;
    const value = normalizeManualQuestion(target?.value ?? '');
    if (target !== null && target.value !== value) {
      target.value = value;
    }
    this.setManualAddQuestion(value);
  }

  onManualAddQuestionPaste(event: ClipboardEvent): void {
    const text = event.clipboardData?.getData('text') ?? '';
    if (!text) return;
    event.preventDefault();
    this.setManualAddQuestion(text);
  }

  submitQueueAdd(): void {
    if (this.addMode() === 'manual') {
      this.createQueuedQuestion();
      return;
    }
    this.importQueuedQuestions();
  }

  createQueuedQuestion(): void {
    this.manualAddSubmitted.set(true);
    const question = normalizeManualQuestion(this.manualAddQuestion()).trim();
    if (this.manualAddQuestionError() !== null) return;
    this.manualAddSubmitting.set(true);
    this.queueService
      .createQueuedQuestion(question)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.manualAddSubmitting.set(false);
          this.manualAddVisible.set(false);
          this.manualAddQuestion.set('');
          this.manualAddSubmitted.set(false);
          this.notifications.success(this.i18n.translate('adminMatrixQueue.addManualAdded'));
          this.loadQueue();
        },
        error: () => {
          this.manualAddSubmitting.set(false);
          this.notifications.error(this.i18n.translate('adminMatrixQueue.addManualError'));
        },
      });
  }

  onImportFileInputChange(event: Event): void {
    const target = event.target as HTMLInputElement | null;
    this.selectImportFiles(target?.files ?? null);
  }

  onImportDragOver(event: DragEvent): void {
    event.preventDefault();
  }

  onImportDrop(event: DragEvent): void {
    event.preventDefault();
    this.selectImportFiles(event.dataTransfer?.files ?? null);
  }

  importQueuedQuestions(): void {
    const file = this.selectedImportFile();
    if (file === null) {
      this.importFileSelectionErrorKey.set('adminMatrixQueue.importOneFileOnly');
      return;
    }
    this.importSubmitting.set(true);
    this.importError.set(null);
    this.importFileSelectionErrorKey.set(null);
    this.queueService
      .importQueuedQuestions(file)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (questions) => {
          this.importSubmitting.set(false);
          this.manualAddVisible.set(false);
          this.manualAddQuestion.set('');
          this.manualAddSubmitted.set(false);
          this.addMode.set('manual');
          this.resetImportState();
          this.notifications.success(
            this.i18n.translate('adminMatrixQueue.importAdded', { count: questions.length }),
          );
          this.loadQueue();
        },
        error: (err: ApiError) => {
          this.importSubmitting.set(false);
          this.importError.set(err);
          this.notifications.error(this.i18n.translate('adminMatrixQueue.importError'));
        },
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
            this.formError.set(null);
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

  createQuestion(payload: AdminMatrixQuestionPayload): void {
    const question = this.selectedQuestion();
    if (question === null) {
      this.notifications.error(this.i18n.translate('adminMatrixQueue.createError'));
      return;
    }
    this.submitting.set(true);
    this.formError.set(null);
    this.queueService
      .createQuestionFromQueue(question.id, payload, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.submitting.set(false);
          this.selectedQuestion.set(null);
          this.formError.set(null);
          this.notifications.success(this.i18n.translate('adminMatrixQueue.created'));
          this.loadQueue();
        },
        error: (err: ApiError) => {
          this.submitting.set(false);
          this.formError.set(err);
          this.notifications.error(this.i18n.translate('adminMatrixQueue.createError'));
        },
      });
  }

  questionStructure(question: QueuedMatrixQuestion): string {
    return [question.grade, question.sheet, question.section, question.subsection]
      .filter((value) => value !== null && value !== '')
      .join(' / ');
  }

  manualAddErrorMessage(): string | null {
    if (!this.manualAddSubmitted()) return null;
    const errorKey = this.manualAddQuestionError();
    if (errorKey === null) return null;
    if (errorKey === 'validation.maxLength') {
      return this.i18n.translate(errorKey, {
        max: String(ADMIN_VALIDATION_LIMITS.shortText),
      });
    }
    return this.i18n.translate(errorKey);
  }

  currentLanguage(): 'ru' | 'en' {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }

  private selectImportFiles(files: FileList | File[] | null): void {
    const selectedFiles = files === null ? [] : Array.from(files);
    this.importError.set(null);
    if (selectedFiles.length !== 1) {
      this.selectedImportFile.set(null);
      this.importFileSelectionErrorKey.set('adminMatrixQueue.importOneFileOnly');
      return;
    }
    this.selectedImportFile.set(selectedFiles[0]);
    this.importFileSelectionErrorKey.set(null);
  }

  private resetImportState(): void {
    this.selectedImportFile.set(null);
    this.importSubmitting.set(false);
    this.importError.set(null);
    this.importFileSelectionErrorKey.set(null);
  }
}

function normalizeManualQuestion(value: string): string {
  return value.replace(LINE_BREAKS_PATTERN, ' ');
}
