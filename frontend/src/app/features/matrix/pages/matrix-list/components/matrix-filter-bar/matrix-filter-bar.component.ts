import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { MatrixLayoutMode } from '../../../../../../core/layout/layout-preferences.service';
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
  readonly layoutMode = input.required<MatrixLayoutMode>();
  readonly canManageContent = input(false);

  readonly searchChange = output<string>();
  readonly onlyPublishedChange = output<boolean>();
  readonly layoutModeChange = output<MatrixLayoutMode>();
  readonly addQuestion = output<void>();

  isListMode(): boolean {
    return this.layoutMode() === 'list';
  }

  isGridMode(): boolean {
    return this.layoutMode() === 'grid';
  }

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

  setLayout(mode: MatrixLayoutMode): void {
    this.layoutModeChange.emit(mode);
  }
}
