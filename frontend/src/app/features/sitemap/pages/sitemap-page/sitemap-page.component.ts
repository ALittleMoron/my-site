import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  computed,
  effect,
  inject,
  signal,
  untracked,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { LanguageCode } from '../../../../core/i18n/i18n.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { SeoService } from '../../../../core/seo/seo.service';
import { SitemapNote, SitemapNotesService } from '../../services/sitemap-notes.service';

interface SitemapNoteLink {
  title: string;
  commands: string[];
}

@Component({
  selector: 'app-sitemap-page',
  standalone: true,
  imports: [RouterLink, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './sitemap-page.component.html',
})
export class SitemapPageComponent implements OnInit {
  private readonly seoService = inject(SeoService);
  private readonly i18n = inject(I18nService);
  private readonly sitemapNotesService = inject(SitemapNotesService);
  private readonly destroyRef = inject(DestroyRef);

  readonly publishedNotes = signal<SitemapNote[]>([]);
  readonly publishedNotesLoading = signal(false);
  readonly publishedNotesError = signal(false);
  readonly language = computed(() => {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  });
  readonly publishedNoteLinks = computed<SitemapNoteLink[]>(() =>
    this.publishedNotes().map((note) => ({
      title: note.title,
      commands: ['/', this.language(), 'notes', note.slug],
    })),
  );

  private readonly publishedNotesLanguageEffect = effect(() => {
    const language = this.i18n.language();
    if (language === null) return;
    untracked(() => this.loadPublishedNotes(language));
  });

  ngOnInit(): void {
    this.seoService.setTranslatedMeta({
      titleKey: 'sitemap.seo.title',
      descriptionKey: 'sitemap.seo.description',
      canonicalPath: '/sitemap',
    });
  }

  private loadPublishedNotes(language: LanguageCode): void {
    this.publishedNotesLoading.set(true);
    this.publishedNotesError.set(false);
    this.sitemapNotesService
      .getPublishedNotes(language)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (notes) => {
          this.publishedNotes.set(notes);
          this.publishedNotesLoading.set(false);
        },
        error: () => {
          this.publishedNotes.set([]);
          this.publishedNotesError.set(true);
          this.publishedNotesLoading.set(false);
        },
      });
  }
}
