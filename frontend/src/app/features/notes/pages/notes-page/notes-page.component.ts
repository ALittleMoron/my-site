import { DOCUMENT, isPlatformBrowser } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  PLATFORM_ID,
  computed,
  effect,
  inject,
  signal,
  untracked,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { combineLatest } from 'rxjs';
import { AuthService } from '../../../../core/auth/auth.service';
import { LanguageCode } from '../../../../core/i18n/i18n.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { ApiError } from '../../../../core/models/api-error.model';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { AnonymousReactionService } from '../../../../core/privacy/anonymous-reaction.service';
import { SeoAlternate, SeoService } from '../../../../core/seo/seo.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import {
  NoteDetail,
  NoteList,
  NotePayload,
  NoteReactionKind,
  NoteStats,
  NoteTag,
  NoteTree,
} from '../../models/notes.model';
import { NotesService } from '../../services/notes.service';
import { NoteDetailComponent } from './components/note-detail/note-detail.component';
import { NoteFormComponent } from './components/note-form/note-form.component';
import { NoteListComponent } from './components/note-list/note-list.component';
import { NotesStatsPanelComponent } from './components/notes-stats-panel/notes-stats-panel.component';
import { NotesSidePanelComponent } from './components/notes-side-panel/notes-side-panel.component';

const PAGE_SIZE = 10;
const SIDE_PANEL_STORAGE_KEY = 'notesSidePanelOpen';
const ENGAGED_VIEW_DELAY_MS = 30_000;
const ENGAGED_VIEW_TICK_MS = 1_000;

interface EngagedViewState {
  slug: string;
  visibleMs: number;
}

@Component({
  selector: 'app-notes-page',
  standalone: true,
  imports: [
    EmptyStateComponent,
    ErrorMessageComponent,
    LoadingSpinnerComponent,
    TranslatePipe,
    NoteDetailComponent,
    NoteFormComponent,
    NoteListComponent,
    NotesStatsPanelComponent,
    NotesSidePanelComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './notes-page.component.html',
  styleUrl: './notes-page.component.scss',
})
export class NotesPageComponent implements OnInit {
  private readonly notesService = inject(NotesService);
  private readonly authService = inject(AuthService);
  private readonly i18n = inject(I18nService);
  private readonly seoService = inject(SeoService);
  private readonly notifications = inject(NotificationService);
  private readonly anonymousReactionService = inject(AnonymousReactionService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly document = inject(DOCUMENT);
  private readonly platformId = inject(PLATFORM_ID);
  private readonly destroyRef = inject(DestroyRef);
  private readonly isBrowser = isPlatformBrowser(this.platformId);
  private engagedViewTimerId: ReturnType<typeof setInterval> | null = null;
  private engagedViewState: EngagedViewState | null = null;
  private readonly trackedEngagedViewSlugs = new Set<string>();
  private languageReloadInitialized = false;

  readonly isAdmin = this.authService.isAdmin;
  readonly sidePanelOpen = signal(this.readSidePanelPreference());
  readonly onlyPublished = signal(true);
  readonly currentSlug = signal<string | null>(null);
  readonly activeTagSlug = signal<string | null>(null);
  readonly searchQuery = signal('');
  readonly publishedFrom = signal('');
  readonly publishedTo = signal('');
  readonly page = signal(1);

  readonly notes = signal<NoteList | null>(null);
  readonly tree = signal<NoteTree>({ folders: [] });
  readonly tags = signal<NoteTag[]>([]);
  readonly selectedNote = signal<NoteDetail | null>(null);
  readonly selectedReaction = signal<NoteReactionKind | null>(null);
  readonly reactionLoading = signal(false);

  readonly listLoading = signal(false);
  readonly listError = signal<ApiError | null>(null);
  readonly detailLoading = signal(false);
  readonly detailError = signal<ApiError | null>(null);

  readonly formVisible = signal(false);
  readonly formNote = signal<NoteDetail | null>(null);
  readonly formError = signal<ApiError | null>(null);
  readonly statsVisible = signal(false);
  readonly stats = signal<NoteStats | null>(null);
  readonly statsLoading = signal(false);
  readonly statsError = signal<ApiError | null>(null);
  readonly statsDateFrom = signal(formatDateInput(daysBefore(new Date(), 30)));
  readonly statsDateTo = signal(formatDateInput(new Date()));

  readonly activeTags = computed(() =>
    [...this.tags()].filter((tag) => tag.deletedAt === null).sort(compareTags),
  );
  readonly activeTag = computed(() => {
    const slug = this.activeTagSlug();
    return slug ? (this.activeTags().find((tag) => tag.slug === slug) ?? null) : null;
  });
  readonly isDetailRoute = computed(() => this.currentSlug() !== null);
  readonly isEmpty = computed(
    () => !this.listLoading() && !this.listError() && (this.notes()?.notes.length ?? 0) === 0,
  );
  readonly hasListFilters = computed(
    () =>
      this.activeTagSlug() !== null ||
      this.searchQuery().trim() !== '' ||
      this.publishedFrom() !== '' ||
      this.publishedTo() !== '',
  );
  readonly dateLocale = computed(() => this.i18n.dateLocale());
  readonly language = computed(() => {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  });

  private readonly languageReloadEffect = effect(() => {
    const language = this.i18n.language();
    if (language === null) return;
    if (!this.languageReloadInitialized) {
      this.languageReloadInitialized = true;
      return;
    }
    untracked(() => this.reloadLocalizedContent());
  });

  ngOnInit(): void {
    this.setNotesListSeo();
    this.loadTags();
    this.loadTree();
    this.destroyRef.onDestroy(() => this.clearEngagedViewTimer());
    combineLatest([this.route.paramMap, this.route.queryParamMap])
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(([params, query]) => {
        const slug = params.get('slug');
        this.currentSlug.set(slug);
        this.activeTagSlug.set(query.get('tag'));
        this.searchQuery.set(query.get('searchQuery') ?? '');
        this.publishedFrom.set(query.get('publishedFrom') ?? '');
        this.publishedTo.set(query.get('publishedTo') ?? '');
        this.page.set(readPage(query.get('page')));
        if (slug) {
          this.loadDetail(slug);
        } else {
          this.setNotesListSeo();
          this.clearEngagedViewTimer();
          this.selectedNote.set(null);
          this.selectedReaction.set(null);
          this.loadNotes();
        }
      });
  }

  toggleSidePanel(): void {
    this.sidePanelOpen.update((value) => {
      const next = !value;
      this.storage()?.setItem(SIDE_PANEL_STORAGE_KEY, String(next));
      return next;
    });
  }

  closeSidePanel(): void {
    this.sidePanelOpen.set(false);
    this.storage()?.setItem(SIDE_PANEL_STORAGE_KEY, 'false');
  }

  setOnlyPublished(value: boolean): void {
    this.onlyPublished.set(value);
    const slug = this.currentSlug();
    if (slug) {
      this.loadDetail(slug);
    } else {
      this.loadNotes();
    }
  }

  openNote(slug: string): void {
    this.router.navigate(this.localizedNoteCommands(slug), {
      queryParams: this.buildListQueryParams({ page: this.page() }),
    });
  }

  backToList(): void {
    this.router.navigate(this.localizedListCommands(), {
      queryParams: this.buildListQueryParams({ page: this.page() }),
    });
  }

  selectTag(slug: string): void {
    this.router.navigate(this.localizedListCommands(), {
      queryParams: this.buildListQueryParams({ page: 1, tagSlug: slug }),
    });
  }

  clearTag(): void {
    this.router.navigate(this.localizedListCommands(), {
      queryParams: this.buildListQueryParams({ page: 1, tagSlug: null }),
    });
  }

  changePage(page: number): void {
    this.router.navigate(this.localizedListCommands(), {
      queryParams: this.buildListQueryParams({ page }),
    });
  }

  setSearchQuery(value: string): void {
    this.searchQuery.set(value);
  }

  setPublishedFrom(value: string): void {
    this.publishedFrom.set(value);
  }

  setPublishedTo(value: string): void {
    this.publishedTo.set(value);
  }

  onSearchInput(event: Event): void {
    this.setSearchQuery(readInputValue(event));
  }

  onPublishedFromInput(event: Event): void {
    this.setPublishedFrom(readInputValue(event));
  }

  onPublishedToInput(event: Event): void {
    this.setPublishedTo(readInputValue(event));
  }

  applyFilters(): void {
    this.router.navigate(this.localizedListCommands(), {
      queryParams: this.buildListQueryParams({ page: 1 }),
    });
  }

  clearListFilters(): void {
    this.searchQuery.set('');
    this.publishedFrom.set('');
    this.publishedTo.set('');
    this.router.navigate(this.localizedListCommands(), { queryParams: { page: 1 } });
  }

  openCreate(): void {
    this.formNote.set(null);
    this.formError.set(null);
    this.formVisible.set(true);
  }

  openEdit(): void {
    this.formNote.set(this.selectedNote());
    this.formError.set(null);
    this.formVisible.set(true);
  }

  closeForm(): void {
    this.formVisible.set(false);
    this.formNote.set(null);
    this.formError.set(null);
  }

  saveNote(payload: NotePayload): void {
    const editing = this.formNote();
    const language = this.currentLanguage();
    const request = editing
      ? this.notesService.updateNote(editing.slug, payload, language)
      : this.notesService.createNote(payload, language);
    request.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (note) => {
        this.notifications.success(this.i18n.translate('notes.notify.saved'));
        this.closeForm();
        this.loadTags();
        this.loadTree();
        this.router.navigate(this.localizedNoteCommands(note.slug));
      },
      error: (err: ApiError) => {
        this.formError.set(err);
        this.notifications.error(this.i18n.translate('notes.notify.saveError'));
      },
    });
  }

  publishNote(): void {
    const note = this.selectedNote();
    if (!note) return;
    this.notesService
      .publishNote(note.slug)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('notes.notify.published'));
          this.loadTree();
          this.loadDetail(note.slug);
        },
        error: (err: ApiError) => {
          this.detailError.set(err);
          this.notifications.error(this.i18n.translate('notes.notify.publishError'));
        },
      });
  }

  unpublishNote(): void {
    const note = this.selectedNote();
    if (!note) return;
    this.notesService
      .unpublishNote(note.slug)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('notes.notify.unpublished'));
          this.loadTree();
          this.loadDetail(note.slug);
        },
        error: (err: ApiError) => {
          this.detailError.set(err);
          this.notifications.error(this.i18n.translate('notes.notify.unpublishError'));
        },
      });
  }

  deleteNote(): void {
    const note = this.selectedNote();
    if (!note) return;
    this.notesService
      .deleteNote(note.slug)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success(this.i18n.translate('notes.notify.deleted'));
          this.loadTree();
          this.router.navigate(this.localizedListCommands());
        },
        error: (err: ApiError) => {
          this.detailError.set(err);
          this.notifications.error(this.i18n.translate('notes.notify.deleteError'));
        },
      });
  }

  selectReaction(kind: NoteReactionKind): void {
    if (!this.isBrowser) return;
    const note = this.selectedNote();
    if (!note || note.publishStatus !== 'Published') return;
    const previousReaction = this.selectedReaction();
    const nextReaction = previousReaction === kind ? null : kind;
    this.reactionLoading.set(true);
    this.notesService
      .setReaction(
        note.slug,
        {
          reactionKind: nextReaction,
          clientToken: this.anonymousReactionService.getOrCreateClientToken(),
        },
        this.currentLanguage(),
      )
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.selectedReaction.set(nextReaction);
          this.anonymousReactionService.setReaction(note.slug, nextReaction);
          this.selectedNote.set(
            applyReactionChange({
              note,
              previousReaction,
              nextReaction,
            }),
          );
          this.reactionLoading.set(false);
        },
        error: () => {
          this.reactionLoading.set(false);
          this.notifications.error(this.i18n.translate('notes.notify.reactionError'));
        },
      });
  }

  toggleStats(): void {
    this.statsVisible.update((visible) => {
      const next = !visible;
      if (next && this.stats() === null) {
        this.loadStats();
      }
      return next;
    });
  }

  setStatsDateFrom(value: string): void {
    this.statsDateFrom.set(value);
  }

  setStatsDateTo(value: string): void {
    this.statsDateTo.set(value);
  }

  loadStats(): void {
    this.statsLoading.set(true);
    this.statsError.set(null);
    this.notesService
      .getStats({
        dateFrom: this.statsDateFrom(),
        dateTo: this.statsDateTo(),
        language: this.currentLanguage(),
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (stats) => {
          this.stats.set(stats);
          this.statsLoading.set(false);
        },
        error: (err: ApiError) => {
          this.statsError.set(err);
          this.statsLoading.set(false);
        },
      });
  }

  exportStatsCsv(): void {
    if (!this.isBrowser) return;
    const stats = this.stats();
    if (!stats) return;
    const csv = buildStatsCsv(stats);
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const link = this.document.createElement('a');
    link.href = url;
    link.download = `notes-stats-${stats.dateFrom}-${stats.dateTo}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  loadNotes(): void {
    this.listLoading.set(true);
    this.listError.set(null);
    this.notesService
      .getNotes({
        page: this.page(),
        pageSize: PAGE_SIZE,
        language: this.currentLanguage(),
        onlyPublished: this.onlyPublished(),
        tagSlug: this.activeTagSlug(),
        publishedFrom: this.publishedFrom() || null,
        publishedTo: this.publishedTo() || null,
        searchQuery: this.normalizedSearchQuery(),
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (notes) => {
          this.notes.set(notes);
          this.listLoading.set(false);
        },
        error: (err: ApiError) => {
          this.listError.set(err);
          this.listLoading.set(false);
        },
      });
  }

  loadDetail(slug: string): void {
    this.clearEngagedViewTimer();
    this.detailLoading.set(true);
    this.detailError.set(null);
    this.notesService
      .getNote(slug, !this.isAdmin(), this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (note) => {
          this.selectedNote.set(note);
          this.setNoteDetailSeo(note);
          this.selectedReaction.set(this.readSelectedReaction(note.slug));
          this.trackPublicView(note);
          this.scheduleEngagedView(note);
          this.detailLoading.set(false);
        },
        error: (err: ApiError) => {
          this.detailError.set(err);
          this.detailLoading.set(false);
        },
      });
  }

  loadTags(): void {
    this.notesService
      .getTags(false, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tags) => this.tags.set(tags),
        error: () => this.tags.set([]),
      });
  }

  loadTree(): void {
    this.notesService
      .getTree(this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tree) => this.tree.set(tree),
        error: () => this.tree.set({ folders: [] }),
      });
  }

  private scheduleEngagedView(note: NoteDetail): void {
    if (!this.isBrowser) return;
    if (this.isAdmin() || note.publishStatus !== 'Published') return;
    if (this.trackedEngagedViewSlugs.has(note.slug)) return;
    this.engagedViewState = {
      slug: note.slug,
      visibleMs: 0,
    };
    this.engagedViewTimerId = setInterval(
      () => this.trackEngagedViewProgress(),
      ENGAGED_VIEW_TICK_MS,
    );
  }

  private trackEngagedViewProgress(): void {
    const state = this.engagedViewState;
    if (state === null || this.document.visibilityState !== 'visible') return;
    state.visibleMs += ENGAGED_VIEW_TICK_MS;
    if (state.visibleMs < ENGAGED_VIEW_DELAY_MS) return;
    this.trackScheduledEngagedView();
  }

  private trackScheduledEngagedView(): void {
    const state = this.engagedViewState;
    if (state === null) return;
    if (this.engagedViewTimerId !== null) {
      clearInterval(this.engagedViewTimerId);
    }
    this.engagedViewTimerId = null;
    this.engagedViewState = null;
    this.notesService
      .trackEngagedView(state.slug, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => this.trackedEngagedViewSlugs.add(state.slug),
        error: () => undefined,
      });
  }

  private trackPublicView(note: NoteDetail): void {
    if (!this.isBrowser) return;
    if (this.isAdmin() || note.publishStatus !== 'Published') return;
    this.notesService
      .trackView(note.slug, this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({ error: () => undefined });
  }

  private clearEngagedViewTimer(): void {
    if (this.engagedViewTimerId !== null) {
      clearInterval(this.engagedViewTimerId);
    }
    this.engagedViewTimerId = null;
    this.engagedViewState = null;
  }

  private buildListQueryParams(params: {
    page: number;
    tagSlug?: string | null;
  }): Record<string, string | number> {
    const queryParams: Record<string, string | number> = { page: params.page };
    const tagSlug = params.tagSlug === undefined ? this.activeTagSlug() : params.tagSlug;
    const searchQuery = this.normalizedSearchQuery();
    if (tagSlug) {
      queryParams['tag'] = tagSlug;
    }
    if (searchQuery) {
      queryParams['searchQuery'] = searchQuery;
    }
    if (this.publishedFrom()) {
      queryParams['publishedFrom'] = this.publishedFrom();
    }
    if (this.publishedTo()) {
      queryParams['publishedTo'] = this.publishedTo();
    }
    return queryParams;
  }

  private normalizedSearchQuery(): string | null {
    const value = this.searchQuery().trim();
    return value === '' ? null : value;
  }

  private reloadLocalizedContent(): void {
    this.loadTags();
    this.loadTree();
    const slug = this.currentSlug();
    if (slug) {
      this.loadDetail(slug);
    } else {
      this.loadNotes();
    }
    if (this.statsVisible()) {
      this.loadStats();
    }
  }

  private currentLanguage(): LanguageCode {
    return this.language();
  }

  private setNotesListSeo(): void {
    const path = '/notes';
    this.seoService.setTranslatedMeta({
      titleKey: 'notes.seo.title',
      descriptionKey: 'notes.seo.description',
      canonicalPath: this.localizedPublicPath(path),
      alternates: this.localizedAlternates(path),
    });
  }

  private setNoteDetailSeo(note: NoteDetail): void {
    const language = this.currentLanguage();
    const path = `/notes/${note.slug}`;
    const metadata = note.metadata;
    const seoTitle = localizedMetadataValue(
      language,
      metadata.seoTitleRu,
      metadata.seoTitleEn,
      note.title,
    );
    const seoDescription = localizedMetadataValue(
      language,
      metadata.seoDescriptionRu,
      metadata.seoDescriptionEn,
      note.excerpt,
    );
    const coverImageUrl = normalizeOptionalString(metadata.coverImageUrl);
    this.seoService.setMeta({
      title: seoTitle,
      description: seoDescription,
      canonicalPath: this.localizedPublicPath(path),
      ogImage: coverImageUrl ?? undefined,
      ogType: 'article',
      alternates: this.localizedAlternates(path),
      structuredData: buildArticleStructuredData({
        note,
        language,
        headline: seoTitle,
        description: seoDescription,
        image: coverImageUrl,
      }),
    });
  }

  private readSelectedReaction(slug: string): NoteReactionKind | null {
    if (!this.isBrowser) return null;
    return toNoteReactionKind(this.anonymousReactionService.getReaction(slug));
  }

  private localizedPublicPath(path: string): string {
    return `/${this.currentLanguage()}${path}`;
  }

  private localizedAlternates(path: string): SeoAlternate[] {
    return [
      { language: 'ru', path: `/ru${path}` },
      { language: 'en', path: `/en${path}` },
    ];
  }

  private localizedListCommands(): string[] {
    return ['/', this.currentLanguage(), 'notes'];
  }

  private localizedNoteCommands(slug: string): string[] {
    return ['/', this.currentLanguage(), 'notes', slug];
  }

  private readSidePanelPreference(): boolean {
    return this.storage()?.getItem(SIDE_PANEL_STORAGE_KEY) === 'true';
  }

  private storage(): Storage | null {
    return this.document.defaultView?.localStorage ?? null;
  }
}

function readPage(value: string | null): number {
  const page = Number(value ?? '1');
  return Number.isFinite(page) && page > 0 ? page : 1;
}

function readInputValue(event: Event): string {
  return (event.target as HTMLInputElement).value;
}

function compareTags(a: NoteTag, b: NoteTag): number {
  return a.name.localeCompare(b.name, 'ru');
}

function toNoteReactionKind(value: string | null): NoteReactionKind | null {
  if (
    value === 'heart' ||
    value === 'fire' ||
    value === 'thinking' ||
    value === 'neutral' ||
    value === 'poop'
  ) {
    return value;
  }
  return null;
}

function localizedMetadataValue(
  language: LanguageCode,
  ru: string | null,
  en: string | null,
  fallback: string,
): string {
  return normalizeOptionalString(language === 'ru' ? ru : en) ?? fallback;
}

function normalizeOptionalString(value: string | null): string | null {
  const normalized = value?.trim() ?? '';
  return normalized === '' ? null : normalized;
}

function buildArticleStructuredData(params: {
  note: NoteDetail;
  language: LanguageCode;
  headline: string;
  description: string;
  image: string | null;
}): Record<string, unknown> {
  const data: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: params.headline,
    description: params.description,
    author: {
      '@type': 'Person',
      name: params.note.authorUsername,
    },
    datePublished: params.note.publishedAt ?? params.note.createdAt,
    dateModified: params.note.updatedAt,
    inLanguage: params.language,
  };
  if (params.image) {
    data['image'] = [params.image];
  }
  return data;
}

function applyReactionChange(params: {
  note: NoteDetail;
  previousReaction: NoteReactionKind | null;
  nextReaction: NoteReactionKind | null;
}): NoteDetail {
  const reactionCounts = { ...params.note.reactionCounts };
  if (params.previousReaction !== null) {
    reactionCounts[params.previousReaction] = Math.max(
      0,
      reactionCounts[params.previousReaction] - 1,
    );
  }
  if (params.nextReaction !== null) {
    reactionCounts[params.nextReaction] += 1;
  }
  return { ...params.note, reactionCounts };
}

function daysBefore(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() - days);
  return result;
}

function formatDateInput(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function buildStatsCsv(stats: NoteStats): string {
  const rows = [
    ['title', 'slug', 'views', 'engaged_views', 'heart', 'fire', 'thinking', 'neutral', 'poop'],
    ...stats.notes.map((note) => [
      note.title,
      note.slug,
      String(note.viewCount),
      String(note.engagedViewCount),
      String(note.reactionCounts.heart),
      String(note.reactionCounts.fire),
      String(note.reactionCounts.thinking),
      String(note.reactionCounts.neutral),
      String(note.reactionCounts.poop),
    ]),
  ];
  return rows.map((row) => row.map(escapeCsvCell).join(',')).join('\n');
}

function escapeCsvCell(value: string): string {
  return `"${value.replaceAll('"', '""')}"`;
}
