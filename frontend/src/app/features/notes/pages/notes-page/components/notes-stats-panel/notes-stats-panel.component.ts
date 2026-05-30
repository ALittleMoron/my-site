import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { ApiError } from '../../../../../../core/models/api-error.model';
import { EmptyStateComponent } from '../../../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../../../shared/ui/loading-spinner/loading-spinner.component';
import { NoteStats } from '../../../../models/notes.model';

@Component({
  selector: 'app-notes-stats-panel',
  standalone: true,
  imports: [EmptyStateComponent, ErrorMessageComponent, LoadingSpinnerComponent, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './notes-stats-panel.component.html',
})
export class NotesStatsPanelComponent {
  readonly stats = input<NoteStats | null>(null);
  readonly loading = input(false);
  readonly error = input<ApiError | null>(null);
  readonly dateFrom = input.required<string>();
  readonly dateTo = input.required<string>();

  readonly dateFromChange = output<string>();
  readonly dateToChange = output<string>();
  readonly refresh = output<void>();
  readonly exportCsv = output<void>();

  onDateFromInput(event: Event): void {
    this.dateFromChange.emit(inputValue(event));
  }

  onDateToInput(event: Event): void {
    this.dateToChange.emit(inputValue(event));
  }
}

function inputValue(event: Event): string {
  return (event.target as HTMLInputElement).value;
}
