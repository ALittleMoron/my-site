import { ChangeDetectionStrategy, Component, computed, inject, input, output } from '@angular/core';
import { LanguageCode } from '../../../../../../core/i18n/i18n.model';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { ApiError } from '../../../../../../core/models/api-error.model';
import { WikiLinkRendererService } from '../../../../../../core/wiki-links/wiki-link-renderer.service';
import { ErrorMessageComponent } from '../../../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../../../shared/ui/loading-spinner/loading-spinner.component';
import {
  ARTICLE_SEO_ANALYSIS_RULES,
  analyzeArticleSeo,
} from '../../../../models/article-seo-analysis';
import { ArticleDetail, ArticleReactionKind } from '../../../../models/articles.model';
import { ArticleSeoPanelComponent } from '../article-seo-panel/article-seo-panel.component';

interface ReactionOption {
  kind: ArticleReactionKind;
  emoji: string;
  labelKey: string;
}

const REACTION_OPTIONS: ReactionOption[] = [
  { kind: 'heart', emoji: '❤️', labelKey: 'enum.articleReaction.heart' },
  { kind: 'fire', emoji: '🔥', labelKey: 'enum.articleReaction.fire' },
  { kind: 'thinking', emoji: '🤔', labelKey: 'enum.articleReaction.thinking' },
  { kind: 'neutral', emoji: '😐', labelKey: 'enum.articleReaction.neutral' },
  { kind: 'poop', emoji: '💩', labelKey: 'enum.articleReaction.poop' },
];

@Component({
  selector: 'app-article-detail',
  standalone: true,
  imports: [
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    TranslatePipe,
    ArticleSeoPanelComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './article-detail.component.html',
})
export class ArticleDetailComponent {
  private readonly wikiLinkRenderer = inject(WikiLinkRendererService);

  readonly article = input<ArticleDetail | null>(null);
  readonly loading = input(false);
  readonly error = input<ApiError | null>(null);
  readonly dateLocale = input.required<string>();
  readonly language = input.required<LanguageCode>();
  readonly canManageContent = input(false);
  readonly selectedReaction = input<ArticleReactionKind | null>(null);
  readonly reactionLoading = input(false);

  readonly back = output<void>();
  readonly edit = output<void>();
  readonly publish = output<void>();
  readonly unpublish = output<void>();
  readonly delete = output<void>();
  readonly tagSelected = output<string>();
  readonly reactionSelected = output<ArticleReactionKind>();

  readonly reactions = REACTION_OPTIONS;

  readonly contentHtml = computed(() => {
    const article = this.article();
    if (!article?.content) return '';
    return this.wikiLinkRenderer.render(article.content, this.language());
  });

  readonly isDraft = computed(() => this.article()?.publishStatus === 'Draft');
  readonly isPublished = computed(() => this.article()?.publishStatus === 'Published');
  readonly seoAnalysis = computed(() => {
    const article = this.article();
    if (!article) return null;
    return analyzeArticleSeo({
      input: {
        slug: article.slug,
        title: article.title,
        content: article.content,
        seoTitle:
          this.language() === 'ru' ? article.metadata.seoTitleRu : article.metadata.seoTitleEn,
        seoDescription:
          this.language() === 'ru'
            ? article.metadata.seoDescriptionRu
            : article.metadata.seoDescriptionEn,
        coverImageUrl: article.metadata.coverImageUrl,
        coverImageAlt:
          this.language() === 'ru'
            ? article.metadata.coverImageAltRu
            : article.metadata.coverImageAltEn,
        missingWikiLinkTargets: [],
        folder: article.folder,
        tags: article.tags,
        language: this.language(),
      },
      rules: ARTICLE_SEO_ANALYSIS_RULES,
    });
  });

  articleDate(): string {
    const article = this.article();
    if (!article) return '';
    return formatDate(article.publishedAt ?? article.updatedAt, this.dateLocale());
  }

  reactionCount(kind: ArticleReactionKind): number {
    const article = this.article();
    if (!article) return 0;
    return article.reactionCounts[kind];
  }
}

function formatDate(value: string, locale: string): string {
  return new Intl.DateTimeFormat(locale, { dateStyle: 'medium' }).format(new Date(value));
}
