import { ChangeDetectionStrategy, Component, computed, inject, input, output } from '@angular/core';
import {
  FoldableTreeComponent,
  FoldableTreeSection,
} from '../../../../../../shared/ui/foldable-tree/foldable-tree.component';
import { I18nService } from '../../../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { NoteTree } from '../../../../models/notes.model';

@Component({
  selector: 'app-notes-side-panel',
  standalone: true,
  imports: [FoldableTreeComponent, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './notes-side-panel.component.html',
})
export class NotesSidePanelComponent {
  private readonly i18n = inject(I18nService);

  readonly tree = input.required<NoteTree>();
  readonly currentSlug = input<string | null>(null);
  readonly noteSelected = output<string>();
  readonly closePanel = output<void>();

  readonly sections = computed<readonly FoldableTreeSection[]>(() => {
    this.i18n.language();
    return this.tree().folders.map((folder) => ({
      key: folder.folder,
      label: folder.folder,
      trailingText: String(folder.notes.length),
      items: folder.notes.map((note) => ({
        key: note.slug,
        label: note.title,
        badgeText: note.publishStatus === 'Draft' ? this.i18n.translate('shared.draft') : null,
      })),
    }));
  });
}
