import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';

@Component({
  selector: 'app-matrix-filter-bar',
  standalone: true,
  imports: [TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-filter-bar.component.html',
})
export class MatrixFilterBarComponent {
  readonly search = input.required<string>();
  readonly onlyPublished = input.required<boolean>();
  readonly canManageContent = input(false);

  readonly searchChange = output<string>();
  readonly onlyPublishedChange = output<boolean>();
  readonly addQuestion = output<void>();
  readonly suggestQuestion = output<void>();

  onSearchInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.searchChange.emit(value);
  }

  clearSearch(): void {
    this.searchChange.emit('');
  }

  toggleOnlyPublished(): void {
    this.onlyPublishedChange.emit(!this.onlyPublished());
  }
}
