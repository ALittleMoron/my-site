import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { renderNoteMarkdown } from '../../../../models/note-wiki-links';
import { NoteTag } from '../../../../models/notes.model';

@Component({
  selector: 'app-note-authoring-preview',
  standalone: true,
  imports: [TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './note-authoring-preview.component.html',
})
export class NoteAuthoringPreviewComponent {
  readonly title = input.required<string>();
  readonly content = input.required<string>();
  readonly tags = input.required<readonly NoteTag[]>();
  readonly coverImageUrl = input.required<string | null>();
  readonly coverImageAlt = input.required<string | null>();
  readonly seoTitle = input.required<string | null>();
  readonly seoDescription = input.required<string | null>();

  readonly contentHtml = computed(() => renderNoteMarkdown(this.content()));
  readonly socialTitle = computed(() => this.seoTitle()?.trim() || this.title().trim());
  readonly socialDescription = computed(() => this.seoDescription()?.trim() ?? '');
}
