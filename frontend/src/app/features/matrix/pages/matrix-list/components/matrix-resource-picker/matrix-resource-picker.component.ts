import { ChangeDetectionStrategy, Component, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { MatrixAttachedResource, MatrixResource } from '../../../../models/matrix-question.model';

export interface MatrixResourceDraft extends MatrixAttachedResource {
  isNew: boolean;
}

@Component({
  selector: 'app-matrix-resource-picker',
  standalone: true,
  imports: [FormsModule, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-resource-picker.component.html',
})
export class MatrixResourcePickerComponent {
  readonly resources = input.required<MatrixResourceDraft[]>();
  readonly searchResults = input<MatrixResource[]>([]);
  readonly searchChange = output<string>();
  readonly resourcesChange = output<MatrixResourceDraft[]>();

  readonly search = signal('');
  readonly newName = signal('');
  readonly newUrl = signal('');

  private nextNewResourceId = -1;

  setSearch(value: string): void {
    this.search.set(value);
    this.searchChange.emit(value);
  }

  attach(resource: MatrixResource): void {
    if (this.resources().some((item) => !item.isNew && item.id === resource.id)) return;
    this.resourcesChange.emit([...this.resources(), { ...resource, context: '', isNew: false }]);
  }

  addNew(): void {
    const name = this.newName().trim();
    const url = this.newUrl().trim();
    if (!name || !url) return;
    this.resourcesChange.emit([
      ...this.resources(),
      { id: this.nextNewResourceId--, name, url, context: '', isNew: true },
    ]);
    this.newName.set('');
    this.newUrl.set('');
  }

  updateContext(index: number, context: string): void {
    this.resourcesChange.emit(
      this.resources().map((resource, currentIndex) =>
        currentIndex === index ? { ...resource, context } : resource,
      ),
    );
  }

  detach(index: number): void {
    this.resourcesChange.emit(this.resources().filter((_, currentIndex) => currentIndex !== index));
  }
}
