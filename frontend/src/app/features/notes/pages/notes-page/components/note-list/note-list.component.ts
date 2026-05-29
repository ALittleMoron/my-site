import { ChangeDetectionStrategy, Component, computed, input, output } from '@angular/core';
import { NoteSummary } from '../../../../models/notes.model';

@Component({
  selector: 'app-note-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './note-list.component.html',
})
export class NoteListComponent {
  readonly notes = input.required<NoteSummary[]>();
  readonly page = input.required<number>();
  readonly totalPages = input.required<number>();
  readonly isAdmin = input(false);

  readonly noteSelected = output<string>();
  readonly tagSelected = output<string>();
  readonly pageChange = output<number>();

  readonly hasPrevious = computed(() => this.page() > 1);
  readonly hasNext = computed(() => this.page() < this.totalPages());

  noteDate(note: NoteSummary): string {
    return formatDate(note.publishedAt ?? note.updatedAt);
  }

  previousPage(): void {
    if (this.hasPrevious()) {
      this.pageChange.emit(this.page() - 1);
    }
  }

  nextPage(): void {
    if (this.hasNext()) {
      this.pageChange.emit(this.page() + 1);
    }
  }
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('ru-RU', { dateStyle: 'medium' }).format(new Date(value));
}
