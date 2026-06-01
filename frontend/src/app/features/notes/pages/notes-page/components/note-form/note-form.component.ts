import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  computed,
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
import { LanguageCode } from '../../../../../../core/i18n/i18n.model';
import { NOTE_SEO_ANALYSIS_RULES, analyzeNoteSeo } from '../../../../models/note-seo-analysis';
import { NoteDetail, NotePayload, NoteTag } from '../../../../models/notes.model';
import { NotesService } from '../../../../services/notes.service';
import { NoteSeoPanelComponent } from '../note-seo-panel/note-seo-panel.component';

interface NoteFormControls {
  titleRu: FormControl<string>;
  titleEn: FormControl<string>;
  contentRu: FormControl<string>;
  contentEn: FormControl<string>;
  slug: FormControl<string>;
  folderRu: FormControl<string>;
  folderEn: FormControl<string>;
  publishStatus: FormControl<'Draft' | 'Published'>;
}

interface TagFormControls {
  nameRu: FormControl<string>;
  nameEn: FormControl<string>;
  slug: FormControl<string>;
}

interface TagDraft extends NoteTag {
  draftNameRu: string;
  draftNameEn: string;
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
  imports: [ReactiveFormsModule, MarkdownEditorComponent, TranslatePipe, NoteSeoPanelComponent],
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
  readonly activeLanguageTab = signal<LanguageCode>('ru');

  readonly form = new FormGroup<NoteFormControls>({
    titleRu: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    titleEn: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    contentRu: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    contentEn: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    slug: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    folderRu: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    folderEn: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    publishStatus: new FormControl<'Draft' | 'Published'>('Draft', { nonNullable: true }),
  });

  readonly newTagForm = new FormGroup<TagFormControls>({
    nameRu: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    nameEn: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    slug: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  });
  readonly formSnapshot = signal(this.form.getRawValue());

  readonly seoAnalysis = computed(() => {
    const value = this.formSnapshot();
    const language = this.activeLanguageTab();
    return analyzeNoteSeo({
      input: {
        slug: value.slug,
        title: language === 'ru' ? value.titleRu : value.titleEn,
        content: language === 'ru' ? value.contentRu : value.contentEn,
        folder: language === 'ru' ? value.folderRu : value.folderEn,
        language,
        tags: this.tags().filter(
          (tag) => tag.deletedAt === null && this.selectedTagIds().has(tag.id),
        ),
      },
      rules: NOTE_SEO_ANALYSIS_RULES,
    });
  });

  ngOnInit(): void {
    const note = this.note();
    if (note) {
      this.slugEdited = true;
      this.form.setValue({
        titleRu: note.translations.ru.title,
        titleEn: note.translations.en.title,
        contentRu: note.translations.ru.content,
        contentEn: note.translations.en.content,
        slug: note.slug,
        folderRu: note.translations.ru.folder,
        folderEn: note.translations.en.folder,
        publishStatus: note.publishStatus,
      });
      this.formSnapshot.set(this.form.getRawValue());
      this.selectedTagIds.set(new Set(note.tags.map((tag) => tag.id)));
    }
    this.form.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => {
      this.formSnapshot.set(this.form.getRawValue());
    });
    this.loadTags();
  }

  onTitleEnInput(): void {
    if (this.slugEdited) return;
    this.form.controls.slug.setValue(slugify(this.form.controls.titleEn.value));
  }

  onSlugInput(): void {
    this.slugEdited = true;
  }

  setActiveLanguageTab(language: LanguageCode): void {
    this.activeLanguageTab.set(language);
  }

  setContentRu(value: string): void {
    this.form.controls.contentRu.setValue(value);
  }

  setContentEn(value: string): void {
    this.form.controls.contentEn.setValue(value);
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

  updateTagDraftNameRu(tagId: number, event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.tags.update((tags) =>
      tags.map((tag) => (tag.id === tagId ? { ...tag, draftNameRu: value } : tag)),
    );
  }

  updateTagDraftNameEn(tagId: number, event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.tags.update((tags) =>
      tags.map((tag) => (tag.id === tagId ? { ...tag, draftNameEn: value } : tag)),
    );
  }

  updateTagDraftSlug(tagId: number, event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.tags.update((tags) =>
      tags.map((tag) => (tag.id === tagId ? { ...tag, draftSlug: value } : tag)),
    );
  }

  onNewTagNameEnInput(): void {
    if (this.newTagSlugEdited) return;
    this.newTagForm.controls.slug.setValue(slugify(this.newTagForm.controls.nameEn.value));
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
    const value = this.newTagForm.getRawValue();
    this.notesService
      .createTag(
        {
          slug: value.slug,
          translations: {
            ru: { name: value.nameRu },
            en: { name: value.nameEn },
          },
        },
        this.currentLanguage(),
      )
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tag) => {
          this.tags.update((tags) => [...tags, toDraft(tag)].sort(compareTags));
          this.newTagForm.reset({ nameRu: '', nameEn: '', slug: '' });
          this.newTagSlugEdited = false;
          this.tagsChanged.emit();
        },
        error: () => this.tagError.set(this.i18n.translate('notes.tags.createError')),
      });
  }

  updateTag(tag: TagDraft): void {
    this.tagError.set(null);
    this.notesService
      .updateTag(
        tag.id,
        {
          slug: tag.draftSlug,
          translations: {
            ru: { name: tag.draftNameRu },
            en: { name: tag.draftNameEn },
          },
        },
        this.currentLanguage(),
      )
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
    this.noteSave.emit({
      slug: value.slug,
      publishStatus: value.publishStatus,
      tagIds: activeTagIds,
      translations: {
        ru: {
          title: value.titleRu,
          content: value.contentRu,
          folder: value.folderRu,
        },
        en: {
          title: value.titleEn,
          content: value.contentEn,
          folder: value.folderEn,
        },
      },
    });
  }

  private loadTags(): void {
    this.notesService
      .getTags(true, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tags) => this.tags.set(tags.map(toDraft).sort(compareTags)),
        error: () => this.tagError.set(this.i18n.translate('notes.tags.loadError')),
      });
  }

  private currentLanguage(): LanguageCode {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }
}

function toDraft(tag: NoteTag): TagDraft {
  return {
    ...tag,
    draftNameRu: tag.translations.ru.name,
    draftNameEn: tag.translations.en.name,
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
