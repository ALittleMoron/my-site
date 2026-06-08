import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { ApiError } from '../../../../../../core/models/api-error.model';
import { EmptyStateComponent } from '../../../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../../../shared/ui/loading-spinner/loading-spinner.component';
import { NoteStats } from '../../../../models/notes.model';
import { LocalizedDatePickerComponent } from '../localized-date-picker/localized-date-picker.component';

@Component({
  selector: 'app-notes-stats-panel',
  standalone: true,
  imports: [
    EmptyStateComponent,
    ErrorMessageComponent,
    LoadingSpinnerComponent,
    LocalizedDatePickerComponent,
    TranslatePipe,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './notes-stats-panel.component.html',
})
export class NotesStatsPanelComponent {
  readonly stats = input<NoteStats | null>(null);
  readonly loading = input(false);
  readonly error = input<ApiError | null>(null);
  readonly dateFrom = input.required<string>();
  readonly dateTo = input.required<string>();
  readonly dateLocale = input.required<string>();
  readonly datePlaceholder = input.required<string>();
  readonly openCalendarLabel = input.required<string>();
  readonly previousMonthLabel = input.required<string>();
  readonly nextMonthLabel = input.required<string>();
  readonly openMonthYearPickerLabel = input.required<string>();
  readonly previousYearLabel = input.required<string>();
  readonly nextYearLabel = input.required<string>();

  readonly dateFromChange = output<string>();
  readonly dateToChange = output<string>();
  readonly refresh = output<void>();
  readonly exportCsv = output<void>();

  setDateFrom(value: string): void {
    this.dateFromChange.emit(value);
  }

  setDateTo(value: string): void {
    this.dateToChange.emit(value);
  }
}
