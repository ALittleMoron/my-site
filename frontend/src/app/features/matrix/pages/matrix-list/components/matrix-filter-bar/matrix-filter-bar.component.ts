import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { MatrixLayoutMode } from '../../../../../../core/layout/layout-preferences.service';

@Component({
  selector: 'app-matrix-filter-bar',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-filter-bar.component.html',
})
export class MatrixFilterBarComponent {
  readonly search = input.required<string>();
  readonly onlyPublished = input.required<boolean>();
  readonly layoutMode = input.required<MatrixLayoutMode>();
  readonly isAdmin = input(false);

  readonly searchChange = output<string>();
  readonly onlyPublishedChange = output<boolean>();
  readonly layoutModeChange = output<MatrixLayoutMode>();

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
