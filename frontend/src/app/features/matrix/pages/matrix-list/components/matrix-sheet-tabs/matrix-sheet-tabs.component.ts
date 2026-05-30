import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';

@Component({
  selector: 'app-matrix-sheet-tabs',
  standalone: true,
  imports: [TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-sheet-tabs.component.html',
})
export class MatrixSheetTabsComponent {
  readonly sheets = input.required<string[]>();
  readonly selectedSheet = input<string | null>(null);

  readonly sheetSelected = output<string>();

  isSelected(sheet: string): boolean {
    return this.selectedSheet() === sheet;
  }

  selectSheet(sheet: string): void {
    this.sheetSelected.emit(sheet);
  }
}
