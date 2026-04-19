import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
  computed,
} from '@angular/core';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged } from 'rxjs';
import { MatrixService } from '../../services/matrix.service';
import { MatrixQuestion } from '../../models/matrix-question.model';
import { ApiError } from '../../../../core/models/api-error.model';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { MatrixQuestionCardComponent } from './components/matrix-question-card/matrix-question-card.component';

@Component({
  selector: 'app-matrix-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    ReactiveFormsModule,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
    MatrixQuestionCardComponent,
  ],
  templateUrl: './matrix-list.component.html',
  styleUrl: './matrix-list.component.scss',
})
export class MatrixListComponent {
  private readonly matrixService = inject(MatrixService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly questions = signal<MatrixQuestion[]>([]);
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly layoutMode = signal<'list' | 'grid'>('list');

  readonly isEmpty = computed(
    () => !this.loading() && !this.error() && this.questions().length === 0,
  );

  readonly searchControl: FormControl<string>;

  constructor() {
    const initialSearch = this.route.snapshot.queryParamMap.get('search') ?? '';
    this.searchControl = new FormControl<string>(initialSearch, { nonNullable: true });

    this.load(initialSearch);

    this.searchControl.valueChanges
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntilDestroyed())
      .subscribe(search => {
        this.router.navigate([], {
          relativeTo: this.route,
          queryParams: { search: search || null },
          queryParamsHandling: 'merge',
        });
        this.load(search);
      });
  }

  load(search = ''): void {
    this.loading.set(true);
    this.error.set(null);
    this.matrixService.getQuestions(search || undefined).subscribe({
      next: questions => {
        this.questions.set(questions);
        this.loading.set(false);
      },
      error: (err: ApiError) => {
        this.error.set(err);
        this.loading.set(false);
      },
    });
  }

  toggleLayout(): void {
    this.layoutMode.update(m => (m === 'list' ? 'grid' : 'list'));
  }
}
