import { ChangeDetectionStrategy, Component, computed, inject, input, output } from '@angular/core';
import { LanguageCode } from '../../../../../../core/i18n/i18n.model';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { ApiError } from '../../../../../../core/models/api-error.model';
import { WikiLinkRendererService } from '../../../../../../core/wiki-links/wiki-link-renderer.service';
import { ErrorMessageComponent } from '../../../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../../../shared/ui/loading-spinner/loading-spinner.component';
import { NOTE_SEO_ANALYSIS_RULES, analyzeNoteSeo } from '../../../../models/note-seo-analysis';
import { NoteDetail, NoteReactionKind } from '../../../../models/notes.model';
import { NoteSeoPanelComponent } from '../note-seo-panel/note-seo-panel.component';

interface ReactionOption {
  kind: NoteReactionKind;
  emoji: string;
  labelKey: string;
}

const REACTION_OPTIONS: ReactionOption[] = [
  { kind: 'heart', emoji: '❤️', labelKey: 'enum.noteReaction.heart' },
  { kind: 'fire', emoji: '🔥', labelKey: 'enum.noteReaction.fire' },
  { kind: 'thinking', emoji: '🤔', labelKey: 'enum.noteReaction.thinking' },
  { kind: 'neutral', emoji: '😐', labelKey: 'enum.noteReaction.neutral' },
  { kind: 'poop', emoji: '💩', labelKey: 'enum.noteReaction.poop' },
];

@Component({
  selector: 'app-note-detail',
  standalone: true,
  imports: [LoadingSpinnerComponent, ErrorMessageComponent, TranslatePipe, NoteSeoPanelComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './note-detail.component.html',
})
export class NoteDetailComponent {
  private readonly wikiLinkRenderer = inject(WikiLinkRendererService);

  readonly note = input<NoteDetail | null>(null);
  readonly loading = input(false);
  readonly error = input<ApiError | null>(null);
  readonly dateLocale = input.required<string>();
  readonly language = input.required<LanguageCode>();
  readonly isAdmin = input(false);
  readonly selectedReaction = input<NoteReactionKind | null>(null);
  readonly reactionLoading = input(false);

  readonly back = output<void>();
  readonly edit = output<void>();
  readonly publish = output<void>();
  readonly unpublish = output<void>();
  readonly delete = output<void>();
  readonly tagSelected = output<string>();
  readonly reactionSelected = output<NoteReactionKind>();

  readonly reactions = REACTION_OPTIONS;

  readonly contentHtml = computed(() => {
    const note = this.note();
    if (!note?.content) return '';
    return this.wikiLinkRenderer.render(note.content, this.language());
  });

  readonly isDraft = computed(() => this.note()?.publishStatus === 'Draft');
  readonly isPublished = computed(() => this.note()?.publishStatus === 'Published');
  readonly seoAnalysis = computed(() => {
    const note = this.note();
    if (!note) return null;
    return analyzeNoteSeo({
      input: {
        slug: note.slug,
        title: note.title,
        content: note.content,
        seoTitle: this.language() === 'ru' ? note.metadata.seoTitleRu : note.metadata.seoTitleEn,
        seoDescription:
          this.language() === 'ru'
            ? note.metadata.seoDescriptionRu
            : note.metadata.seoDescriptionEn,
        coverImageUrl: note.metadata.coverImageUrl,
        coverImageAlt:
          this.language() === 'ru' ? note.metadata.coverImageAltRu : note.metadata.coverImageAltEn,
        missingWikiLinkTargets: [],
        folder: note.folder,
        tags: note.tags,
        language: this.language(),
      },
      rules: NOTE_SEO_ANALYSIS_RULES,
    });
  });

  noteDate(): string {
    const note = this.note();
    if (!note) return '';
    return formatDate(note.publishedAt ?? note.updatedAt, this.dateLocale());
  }

  reactionCount(kind: NoteReactionKind): number {
    const note = this.note();
    if (!note) return 0;
    return note.reactionCounts[kind];
  }
}

function formatDate(value: string, locale: string): string {
  return new Intl.DateTimeFormat(locale, { dateStyle: 'medium' }).format(new Date(value));
}
