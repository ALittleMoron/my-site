import { ChangeDetectionStrategy, Component, computed, inject, input } from '@angular/core';
import { LanguageCode } from '../../../../../../core/i18n/i18n.model';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { WikiLinkRendererService } from '../../../../../../core/wiki-links/wiki-link-renderer.service';
import { ArticleTag } from '../../../../models/articles.model';

@Component({
  selector: 'app-article-authoring-preview',
  standalone: true,
  imports: [TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './article-authoring-preview.component.html',
})
export class ArticleAuthoringPreviewComponent {
  private readonly wikiLinkRenderer = inject(WikiLinkRendererService);

  readonly title = input.required<string>();
  readonly content = input.required<string>();
  readonly tags = input.required<readonly ArticleTag[]>();
  readonly coverImageUrl = input.required<string | null>();
  readonly coverImageAlt = input.required<string | null>();
  readonly seoTitle = input.required<string | null>();
  readonly seoDescription = input.required<string | null>();
  readonly language = input.required<LanguageCode>();

  readonly contentHtml = computed(() =>
    this.wikiLinkRenderer.render(this.content(), this.language()),
  );
  readonly socialTitle = computed(() => this.seoTitle()?.trim() || this.title().trim());
  readonly socialDescription = computed(() => this.seoDescription()?.trim() ?? '');
}
