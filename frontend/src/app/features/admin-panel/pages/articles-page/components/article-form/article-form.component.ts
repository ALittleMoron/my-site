import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  computed,
  effect,
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
import { AdminControlValidationStateDirective } from '../../../../directives/admin-control-validation-state.directive';
import {
  ADMIN_VALIDATION_LIMITS,
  controlInvalid,
  httpUrlValidator,
  isRequiredShortText,
  isSlug,
  slugValidator,
  trimRequired,
  validationMessage,
} from '../../../../utils/admin-validation';

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

type ArticleField = keyof ArticleFormControls;
type RequiredTagField = 'nameRu' | 'nameEn' | 'slug';
type TagDraftField = 'nameRu' | 'nameEn' | 'slug';

@Component({
  selector: 'app-admin-article-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MarkdownEditorComponent,
    TranslatePipe,
    ArticleAuthoringPreviewComponent,
    ArticleSeoPanelComponent,
    AdminControlValidationStateDirective,
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
  readonly validationLimits = ADMIN_VALIDATION_LIMITS;

  readonly form = new FormGroup<ArticleFormControls>({
    titleRu: new FormControl('', {
      nonNullable: true,
      validators: [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)],
    }),
    titleEn: new FormControl('', {
      nonNullable: true,
      validators: [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)],
    }),
    contentRu: new FormControl('', {
      nonNullable: true,
      validators: [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.articleContent)],
    }),
    contentEn: new FormControl('', {
      nonNullable: true,
      validators: [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.articleContent)],
    }),
    slug: new FormControl('', {
      nonNullable: true,
      validators: [
        trimRequired,
        Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText),
        slugValidator,
      ],
    }),
    folderRu: new FormControl('', {
      nonNullable: true,
      validators: [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)],
    }),
    folderEn: new FormControl('', {
      nonNullable: true,
      validators: [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)],
    }),
    seoTitleRu: new FormControl('', {
      nonNullable: true,
      validators: Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText),
    }),
    seoTitleEn: new FormControl('', {
      nonNullable: true,
      validators: Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText),
    }),
    seoDescriptionRu: new FormControl('', {
      nonNullable: true,
      validators: Validators.maxLength(ADMIN_VALIDATION_LIMITS.seoDescription),
    }),
    seoDescriptionEn: new FormControl('', {
      nonNullable: true,
      validators: Validators.maxLength(ADMIN_VALIDATION_LIMITS.seoDescription),
    }),
    coverImageUrl: new FormControl('', {
      nonNullable: true,
      validators: [Validators.maxLength(ADMIN_VALIDATION_LIMITS.url), httpUrlValidator],
    }),
    coverImageAltRu: new FormControl('', {
      nonNullable: true,
      validators: Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText),
    }),
    coverImageAltEn: new FormControl('', {
      nonNullable: true,
      validators: Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText),
    }),
    publishStatus: new FormControl<'Draft' | 'Published'>('Draft', { nonNullable: true }),
  });

  readonly newTagForm = new FormGroup<TagFormControls>({
    nameRu: new FormControl('', {
      nonNullable: true,
      validators: [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)],
    }),
    nameEn: new FormControl('', {
      nonNullable: true,
      validators: [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)],
    }),
    slug: new FormControl('', {
      nonNullable: true,
      validators: [
        trimRequired,
        Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText),
        slugValidator,
      ],
    }),
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

  constructor() {
    effect(() => {
      this.applyArticle(this.article());
    });
  }

  ngOnInit(): void {
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
    if (this.tagDraftInvalid(tag)) return;
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

  articleFieldInvalid(field: ArticleField): boolean {
    return controlInvalid(this.form.controls[field], this.formSubmitted());
  }

  articleFieldMessage(field: ArticleField): string | null {
    return validationMessage(this.form.controls[field], this.i18n);
  }

  newTagFieldInvalid(field: RequiredTagField): boolean {
    return controlInvalid(this.newTagForm.controls[field], this.newTagFormSubmitted());
  }

  newTagFieldMessage(field: RequiredTagField): string | null {
    return validationMessage(this.newTagForm.controls[field], this.i18n);
  }

  tagDraftFieldInvalid(tag: TagDraft, field: TagDraftField): boolean {
    if (this.isTagDeleted(tag)) return false;
    return this.tagDraftFieldMessage(tag, field) !== null;
  }

  tagDraftFieldMessage(tag: TagDraft, field: TagDraftField): string | null {
    const value = this.tagDraftFieldValue(tag, field);
    if (field === 'slug') {
      return isSlug(value) ? null : this.i18n.translate('validation.slug');
    }
    if (value.trim() === '') return this.i18n.translate('validation.required');
    return isRequiredShortText(value)
      ? null
      : this.i18n.translate('validation.maxLength', {
          max: String(ADMIN_VALIDATION_LIMITS.shortText),
        });
  }

  tagDraftInvalid(tag: TagDraft): boolean {
    return (
      this.tagDraftFieldInvalid(tag, 'nameRu') ||
      this.tagDraftFieldInvalid(tag, 'nameEn') ||
      this.tagDraftFieldInvalid(tag, 'slug')
    );
  }

  languageTabInvalid(language: LanguageCode): boolean {
    const fields =
      language === 'ru'
        ? ([
            'titleRu',
            'folderRu',
            'seoTitleRu',
            'seoDescriptionRu',
            'coverImageAltRu',
            'contentRu',
          ] satisfies ArticleField[])
        : ([
            'titleEn',
            'folderEn',
            'seoTitleEn',
            'seoDescriptionEn',
            'coverImageAltEn',
            'contentEn',
          ] satisfies ArticleField[]);
    return fields.some((field) => this.articleFieldInvalid(field));
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

  private applyArticle(article: ArticleDetail | null): void {
    if (article === null) {
      this.slugEdited = false;
      this.form.reset({
        titleRu: '',
        titleEn: '',
        contentRu: '',
        contentEn: '',
        slug: '',
        folderRu: '',
        folderEn: '',
        seoTitleRu: '',
        seoTitleEn: '',
        seoDescriptionRu: '',
        seoDescriptionEn: '',
        coverImageUrl: '',
        coverImageAltRu: '',
        coverImageAltEn: '',
        publishStatus: 'Draft',
      });
      this.formSnapshot.set(this.form.getRawValue());
      this.selectedTagIds.set(new Set<number>());
      return;
    }
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

  private tagDraftFieldValue(tag: TagDraft, field: TagDraftField): string {
    if (field === 'nameRu') return tag.draftNameRu;
    if (field === 'nameEn') return tag.draftNameEn;
    return tag.draftSlug;
  }
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
