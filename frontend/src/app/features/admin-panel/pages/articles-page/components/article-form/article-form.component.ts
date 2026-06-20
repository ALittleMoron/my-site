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
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  ValidationErrors,
} from '@angular/forms';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { I18nService } from '../../../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { LanguageCode } from '../../../../../../core/i18n/i18n.model';
import { MediaUploadService } from '../../../../../../core/uploads/media-upload.service';
import {
  WikiLinkTargetLookup,
  findMissingWikiLinkTargets,
} from '../../../../../../core/wiki-links/wiki-links';
import { WikiLinkTargetsService } from '../../../../../../core/wiki-links/wiki-link-targets.service';
import {
  ARTICLE_SEO_ANALYSIS_RULES,
  analyzeArticleSeo,
} from '../../../../models/article-seo-analysis';
import {
  ArticleDetail,
  ArticleMetadata,
  ArticlePayload,
  ArticleTag,
} from '../../../../models/article-workspace.model';
import { ArticleWorkspaceService } from '../../../../services/article-workspace.service';
import { slugify } from '../../../../../../shared/utils/slugify';
import { ArticleAuthoringPreviewComponent } from '../article-authoring-preview/article-authoring-preview.component';
import { ArticleSeoPanelComponent } from '../article-seo-panel/article-seo-panel.component';

interface ArticleFormControls {
  titleRu: FormControl<string>;
  titleEn: FormControl<string>;
  contentRu: FormControl<string>;
  contentEn: FormControl<string>;
  slug: FormControl<string>;
  folderRu: FormControl<string>;
  folderEn: FormControl<string>;
  seoTitleRu: FormControl<string>;
  seoTitleEn: FormControl<string>;
  seoDescriptionRu: FormControl<string>;
  seoDescriptionEn: FormControl<string>;
  coverImageUrl: FormControl<string>;
  coverImageAltRu: FormControl<string>;
  coverImageAltEn: FormControl<string>;
  publishStatus: FormControl<'Draft' | 'Published'>;
}

interface ArticleMetadataFormValue {
  seoTitleRu: string;
  seoTitleEn: string;
  seoDescriptionRu: string;
  seoDescriptionEn: string;
  coverImageUrl: string;
  coverImageAltRu: string;
  coverImageAltEn: string;
}

interface ArticlePreviewState {
  title: string;
  content: string;
  tags: readonly ArticleTag[];
  coverImageUrl: string | null;
  coverImageAlt: string | null;
  seoTitle: string | null;
  seoDescription: string | null;
  language: LanguageCode;
}

interface TagFormControls {
  nameRu: FormControl<string>;
  nameEn: FormControl<string>;
  slug: FormControl<string>;
}

interface TagDraft extends ArticleTag {
  draftNameRu: string;
  draftNameEn: string;
  draftSlug: string;
}

type RequiredArticleField =
  | 'titleRu'
  | 'titleEn'
  | 'contentRu'
  | 'contentEn'
  | 'slug'
  | 'folderRu'
  | 'folderEn';
type RequiredTagField = 'nameRu' | 'nameEn' | 'slug';

@Component({
  selector: 'app-admin-article-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MarkdownEditorComponent,
    TranslatePipe,
    ArticleAuthoringPreviewComponent,
    ArticleSeoPanelComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './article-form.component.html',
  styleUrl: './article-form.component.scss',
})
export class ArticleFormComponent implements OnInit {
  private readonly articlesService = inject(ArticleWorkspaceService);
  private readonly mediaUpload = inject(MediaUploadService);
  private readonly wikiLinkTargetsService = inject(WikiLinkTargetsService);
  private readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);
  private slugEdited = false;
  private newTagSlugEdited = false;

  readonly article = input<ArticleDetail | null>(null);
  readonly articleSave = output<ArticlePayload>();
  readonly formCancel = output<void>();
  readonly tagsChanged = output<void>();

  readonly tags = signal<TagDraft[]>([]);
  readonly selectedTagIds = signal<ReadonlySet<number>>(new Set<number>());
  readonly availableWikiLinkTargets = signal<WikiLinkTargetLookup | null>(null);
  readonly tagError = signal<string | null>(null);
  readonly activeLanguageTab = signal<LanguageCode>('ru');
  readonly formSubmitted = signal(false);
  readonly newTagFormSubmitted = signal(false);

  readonly form = new FormGroup<ArticleFormControls>({
    titleRu: new FormControl('', { nonNullable: true, validators: [trimRequired] }),
    titleEn: new FormControl('', { nonNullable: true, validators: [trimRequired] }),
    contentRu: new FormControl('', { nonNullable: true, validators: [trimRequired] }),
    contentEn: new FormControl('', { nonNullable: true, validators: [trimRequired] }),
    slug: new FormControl('', { nonNullable: true, validators: [trimRequired] }),
    folderRu: new FormControl('', { nonNullable: true, validators: [trimRequired] }),
    folderEn: new FormControl('', { nonNullable: true, validators: [trimRequired] }),
    seoTitleRu: new FormControl('', { nonNullable: true }),
    seoTitleEn: new FormControl('', { nonNullable: true }),
    seoDescriptionRu: new FormControl('', { nonNullable: true }),
    seoDescriptionEn: new FormControl('', { nonNullable: true }),
    coverImageUrl: new FormControl('', { nonNullable: true }),
    coverImageAltRu: new FormControl('', { nonNullable: true }),
    coverImageAltEn: new FormControl('', { nonNullable: true }),
    publishStatus: new FormControl<'Draft' | 'Published'>('Draft', { nonNullable: true }),
  });

  readonly newTagForm = new FormGroup<TagFormControls>({
    nameRu: new FormControl('', { nonNullable: true, validators: [trimRequired] }),
    nameEn: new FormControl('', { nonNullable: true, validators: [trimRequired] }),
    slug: new FormControl('', { nonNullable: true, validators: [trimRequired] }),
  });
  readonly formSnapshot = signal(this.form.getRawValue());

  readonly seoAnalysis = computed(() => {
    const value = this.formSnapshot();
    const language = this.activeLanguageTab();
    const metadata = toMetadata(value);
    return analyzeArticleSeo({
      input: {
        slug: value.slug,
        title: language === 'ru' ? value.titleRu : value.titleEn,
        content: language === 'ru' ? value.contentRu : value.contentEn,
        seoTitle: language === 'ru' ? metadata.seoTitleRu : metadata.seoTitleEn,
        seoDescription: language === 'ru' ? metadata.seoDescriptionRu : metadata.seoDescriptionEn,
        coverImageUrl: metadata.coverImageUrl,
        coverImageAlt: language === 'ru' ? metadata.coverImageAltRu : metadata.coverImageAltEn,
        missingWikiLinkTargets: missingWikiLinkTargets({
          markdown: language === 'ru' ? value.contentRu : value.contentEn,
          availableTargets: this.availableWikiLinkTargets(),
        }),
        folder: language === 'ru' ? value.folderRu : value.folderEn,
        language,
        tags: this.activeTags(),
      },
      rules: ARTICLE_SEO_ANALYSIS_RULES,
    });
  });
  readonly activePreview = computed<ArticlePreviewState>(() => {
    const value = this.formSnapshot();
    const language = this.activeLanguageTab();
    const metadata = toMetadata(value);
    return {
      title: language === 'ru' ? value.titleRu : value.titleEn,
      content: language === 'ru' ? value.contentRu : value.contentEn,
      tags: this.activeTags(),
      coverImageUrl: metadata.coverImageUrl,
      coverImageAlt: language === 'ru' ? metadata.coverImageAltRu : metadata.coverImageAltEn,
      seoTitle: language === 'ru' ? metadata.seoTitleRu : metadata.seoTitleEn,
      seoDescription: language === 'ru' ? metadata.seoDescriptionRu : metadata.seoDescriptionEn,
      language,
    };
  });

  ngOnInit(): void {
    const article = this.article();
    if (article) {
      this.slugEdited = true;
      this.form.setValue({
        titleRu: article.translations.ru.title,
        titleEn: article.translations.en.title,
        contentRu: article.translations.ru.content,
        contentEn: article.translations.en.content,
        slug: article.slug,
        folderRu: article.translations.ru.folder,
        folderEn: article.translations.en.folder,
        seoTitleRu: article.metadata.seoTitleRu ?? '',
        seoTitleEn: article.metadata.seoTitleEn ?? '',
        seoDescriptionRu: article.metadata.seoDescriptionRu ?? '',
        seoDescriptionEn: article.metadata.seoDescriptionEn ?? '',
        coverImageUrl: article.metadata.coverImageUrl ?? '',
        coverImageAltRu: article.metadata.coverImageAltRu ?? '',
        coverImageAltEn: article.metadata.coverImageAltEn ?? '',
        publishStatus: article.publishStatus,
      });
      this.formSnapshot.set(this.form.getRawValue());
      this.selectedTagIds.set(new Set(article.tags.map((tag) => tag.id)));
    }
    this.form.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => {
      this.formSnapshot.set(this.form.getRawValue());
    });
    this.loadTags();
    this.loadWikiLinkTargets();
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
    this.updateMarkdownContent(this.form.controls.contentRu, value);
  }

  setContentEn(value: string): void {
    this.updateMarkdownContent(this.form.controls.contentEn, value);
  }

  setPublishStatusFromEvent(event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.form.controls.publishStatus.setValue(checked ? 'Draft' : 'Published');
  }

  uploadCoverImage(event: Event): void {
    const files = (event.target as HTMLInputElement).files;
    const file = files?.item?.(0) ?? files?.[0];
    if (!file) return;
    this.mediaUpload
      .uploadMediaFile(file)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((accessUrl) => {
        this.form.controls.coverImageUrl.setValue(accessUrl);
      });
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

  isTagDeleted(tag: ArticleTag): boolean {
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
    this.newTagFormSubmitted.set(true);
    if (this.newTagForm.invalid) {
      this.newTagForm.markAllAsTouched();
      return;
    }
    this.tagError.set(null);
    const value = this.newTagForm.getRawValue();
    this.articlesService
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
          this.newTagFormSubmitted.set(false);
          this.tagsChanged.emit();
        },
        error: () => this.tagError.set(this.i18n.translate('articles.tags.createError')),
      });
  }

  updateTag(tag: TagDraft): void {
    this.tagError.set(null);
    this.articlesService
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
        error: () => this.tagError.set(this.i18n.translate('articles.tags.saveError')),
      });
  }

  deleteTag(tagId: number): void {
    this.tagError.set(null);
    this.articlesService
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
        error: () => this.tagError.set(this.i18n.translate('articles.tags.deleteError')),
      });
  }

  restoreTag(tagId: number): void {
    this.tagError.set(null);
    this.articlesService
      .restoreTag(tagId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.loadTags();
          this.tagsChanged.emit();
        },
        error: () => this.tagError.set(this.i18n.translate('articles.tags.restoreError')),
      });
  }

  submit(): void {
    this.formSubmitted.set(true);
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    const activeTagIds = this.tags()
      .filter((tag) => !this.isTagDeleted(tag) && this.selectedTagIds().has(tag.id))
      .map((tag) => tag.id);
    this.articleSave.emit({
      slug: value.slug,
      publishStatus: value.publishStatus,
      tagIds: activeTagIds,
      metadata: toMetadata(value),
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

  articleFieldInvalid(field: RequiredArticleField): boolean {
    const control = this.form.controls[field];
    return control.invalid && (this.formSubmitted() || control.touched);
  }

  newTagFieldInvalid(field: RequiredTagField): boolean {
    const control = this.newTagForm.controls[field];
    return control.invalid && (this.newTagFormSubmitted() || control.touched);
  }

  private loadTags(): void {
    this.articlesService
      .getTags(true, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tags) => this.tags.set(tags.map(toDraft).sort(compareTags)),
        error: () => this.tagError.set(this.i18n.translate('articles.tags.loadError')),
      });
  }

  private loadWikiLinkTargets(): void {
    this.wikiLinkTargetsService
      .getTargets(this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (targets) => this.availableWikiLinkTargets.set(targets),
        error: () => this.availableWikiLinkTargets.set(null),
      });
  }

  private activeTags(): ArticleTag[] {
    return this.tags().filter((tag) => tag.deletedAt === null && this.selectedTagIds().has(tag.id));
  }

  private currentLanguage(): LanguageCode {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }

  private updateMarkdownContent(control: FormControl<string>, value: string): void {
    control.setValue(value);
    control.markAsDirty();
    control.markAsTouched();
  }
}

function trimRequired(control: AbstractControl<string>): ValidationErrors | null {
  return control.value.trim() === '' ? { required: true } : null;
}

function toMetadata(value: ArticleMetadataFormValue): ArticleMetadata {
  return {
    seoTitleRu: optionalText(value.seoTitleRu),
    seoTitleEn: optionalText(value.seoTitleEn),
    seoDescriptionRu: optionalText(value.seoDescriptionRu),
    seoDescriptionEn: optionalText(value.seoDescriptionEn),
    coverImageUrl: optionalText(value.coverImageUrl),
    coverImageAltRu: optionalText(value.coverImageAltRu),
    coverImageAltEn: optionalText(value.coverImageAltEn),
  };
}

function optionalText(value: string): string | null {
  const trimmed = value.trim();
  return trimmed === '' ? null : trimmed;
}

function toDraft(tag: ArticleTag): TagDraft {
  return {
    ...tag,
    draftNameRu: tag.translations.ru.name,
    draftNameEn: tag.translations.en.name,
    draftSlug: tag.slug,
  };
}

function missingWikiLinkTargets(params: {
  markdown: string;
  availableTargets: WikiLinkTargetLookup | null;
}): string[] {
  if (params.availableTargets === null) return [];
  return findMissingWikiLinkTargets({
    markdown: params.markdown,
    availableTargets: params.availableTargets,
  });
}

function compareTags(a: ArticleTag, b: ArticleTag): number {
  return a.name.localeCompare(b.name, 'ru');
}
