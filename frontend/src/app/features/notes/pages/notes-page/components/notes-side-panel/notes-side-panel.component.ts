import { ChangeDetectionStrategy, Component, input, output, signal } from '@angular/core';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { NoteTree, NoteTreeFolder } from '../../../../models/notes.model';

@Component({
  selector: 'app-notes-side-panel',
  standalone: true,
  imports: [TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './notes-side-panel.component.html',
})
export class NotesSidePanelComponent {
  readonly tree = input.required<NoteTree>();
  readonly currentSlug = input<string | null>(null);
  readonly noteSelected = output<string>();
  readonly closePanel = output<void>();

  readonly expandedFolders = signal<ReadonlySet<string>>(new Set<string>());

  isExpanded(folder: string): boolean {
    return this.expandedFolders().has(folder);
  }

  toggleFolder(folder: string): void {
    this.expandedFolders.update((current) => {
      const next = new Set(current);
      if (next.has(folder)) {
        next.delete(folder);
      } else {
        next.add(folder);
      }
      return next;
    });
  }

  folderNoteCount(folder: NoteTreeFolder): number {
    return folder.notes.length;
  }
}
