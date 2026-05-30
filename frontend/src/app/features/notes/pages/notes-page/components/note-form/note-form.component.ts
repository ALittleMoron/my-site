import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  inject,
  input,
  output,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { I18nService } from '../../../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { NoteDetail, NotePayload, NoteTag } from '../../../../models/notes.model';
import { NotesService } from '../../../../services/notes.service';

interface NoteFormControls {
  title: FormControl<string>;
  content: FormControl<string>;
  slug: FormControl<string>;
  folder: FormControl<string>;
  publishStatus: FormControl<'Draft' | 'Published'>;
}

interface TagFormControls {
  name: FormControl<string>;
  slug: FormControl<string>;
}

interface TagDraft extends NoteTag {
  draftName: string;
  draftSlug: string;
}

const CYRILLIC_TO_LATIN: Record<string, string> = {
  а: 'a',
  б: 'b',
  в: 'v',
  г: 'g',
  д: 'd',
  е: 'e',
  ё: 'e',
  ж: 'zh',
  з: 'z',
  и: 'i',
  й: 'y',
  к: 'k',
  л: 'l',
  м: 'm',
  н: 'n',
  о: 'o',
  п: 'p',
  р: 'r',
  с: 's',
  т: 't',
  у: 'u',
  ф: 'f',
  х: 'h',
  ц: 'c',
  ч: 'ch',
  ш: 'sh',
  щ: 'sch',
  ъ: '',
  ы: 'y',
  ь: '',
  э: 'e',
  ю: 'yu',
  я: 'ya',
};

@Component({
  selector: 'app-note-form',
  standalone: true,
  imports: [ReactiveFormsModule, MarkdownEditorComponent, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './note-form.component.html',
})
export class NoteFormComponent implements OnInit {
  private readonly notesService = inject(NotesService);
  private readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);
  private slugEdited = false;
  private newTagSlugEdited = false;

  readonly note = input<NoteDetail | null>(null);
  readonly noteSave = output<NotePayload>();
  readonly formCancel = output<void>();
  readonly tagsChanged = output<void>();

  readonly tags = signal<TagDraft[]>([]);
  readonly selectedTagIds = signal<ReadonlySet<number>>(new Set<number>());
  readonly tagError = signal<string | null>(null);

  readonly form = new FormGroup<NoteFormControls>({
    title: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    content: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    slug: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    folder: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    publishStatus: new FormControl<'Draft' | 'Published'>('Draft', { nonNullable: true }),
  });

  readonly newTagForm = new FormGroup<TagFormControls>({
    name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    slug: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  });

  ngOnInit(): void {
    const note = this.note();
    if (note) {
      this.slugEdited = true;
      this.form.setValue({
        title: note.title,
        content: note.content,
        slug: note.slug,
        folder: note.folder,
        publishStatus: note.publishStatus,
      });
      this.selectedTagIds.set(new Set(note.tags.map((tag) => tag.id)));
    }
    this.loadTags();
  }

  onTitleInput(): void {
    if (this.slugEdited) return;
    this.form.controls.slug.setValue(slugify(this.form.controls.title.value));
  }

  onSlugInput(): void {
    this.slugEdited = true;
  }

  setContent(value: string): void {
    this.form.controls.content.setValue(value);
  }

  setPublishStatusFromEvent(event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.form.controls.publishStatus.setValue(checked ? 'Draft' : 'Published');
  }

  toggleTag(tagId: number, event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.selectedTagIds.update((current) => {
      const next = new Set(current);
      if (checked) {
        next.add(tagId);
      } else {
        next.delete(tagId);
      }
      return next;
    });
  }

  isTagSelected(tagId: number): boolean {
    return this.selectedTagIds().has(tagId);
  }

  isTagDeleted(tag: NoteTag): boolean {
    return tag.deletedAt !== null;
  }

  updateTagDraftName(tagId: number, event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.tags.update((tags) =>
      tags.map((tag) => (tag.id === tagId ? { ...tag, draftName: value } : tag)),
    );
  }

  updateTagDraftSlug(tagId: number, event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.tags.update((tags) =>
      tags.map((tag) => (tag.id === tagId ? { ...tag, draftSlug: value } : tag)),
    );
  }

  onNewTagNameInput(): void {
    if (this.newTagSlugEdited) return;
    this.newTagForm.controls.slug.setValue(slugify(this.newTagForm.controls.name.value));
  }

  onNewTagSlugInput(): void {
    this.newTagSlugEdited = true;
  }

  createTag(): void {
    if (this.newTagForm.invalid) {
      this.newTagForm.markAllAsTouched();
      return;
    }
    this.tagError.set(null);
    this.notesService
      .createTag(this.newTagForm.getRawValue())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tag) => {
          this.tags.update((tags) => [...tags, toDraft(tag)].sort(compareTags));
          this.newTagForm.reset({ name: '', slug: '' });
          this.newTagSlugEdited = false;
          this.tagsChanged.emit();
        },
        error: () => this.tagError.set(this.i18n.translate('notes.tags.createError')),
      });
  }

  updateTag(tag: TagDraft): void {
    this.tagError.set(null);
    this.notesService
      .updateTag(tag.id, { name: tag.draftName, slug: tag.draftSlug })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (updated) => {
          this.tags.update((tags) =>
            tags
              .map((item) => (item.id === updated.id ? toDraft(updated) : item))
              .sort(compareTags),
          );
          this.tagsChanged.emit();
        },
        error: () => this.tagError.set(this.i18n.translate('notes.tags.saveError')),
      });
  }

  deleteTag(tagId: number): void {
    this.tagError.set(null);
    this.notesService
      .deleteTag(tagId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.loadTags();
          this.selectedTagIds.update((current) => {
            const next = new Set(current);
            next.delete(tagId);
            return next;
          });
          this.tagsChanged.emit();
        },
        error: () => this.tagError.set(this.i18n.translate('notes.tags.deleteError')),
      });
  }

  restoreTag(tagId: number): void {
    this.tagError.set(null);
    this.notesService
      .restoreTag(tagId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.loadTags();
          this.tagsChanged.emit();
        },
        error: () => this.tagError.set(this.i18n.translate('notes.tags.restoreError')),
      });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    const activeTagIds = this.tags()
      .filter((tag) => !this.isTagDeleted(tag) && this.selectedTagIds().has(tag.id))
      .map((tag) => tag.id);
    this.noteSave.emit({ ...value, tagIds: activeTagIds });
  }

  private loadTags(): void {
    this.notesService
      .getTags(true)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tags) => this.tags.set(tags.map(toDraft).sort(compareTags)),
        error: () => this.tagError.set(this.i18n.translate('notes.tags.loadError')),
      });
  }
}

function toDraft(tag: NoteTag): TagDraft {
  return {
    ...tag,
    draftName: tag.name,
    draftSlug: tag.slug,
  };
}

function compareTags(a: NoteTag, b: NoteTag): number {
  return a.name.localeCompare(b.name, 'ru');
}

function slugify(value: string): string {
  const transliterated = value
    .toLowerCase()
    .split('')
    .map((char) => CYRILLIC_TO_LATIN[char] ?? char)
    .join('');
  return transliterated
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
