import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import {
  ActivatedRoute,
  ParamMap,
  Router,
  convertToParamMap,
  provideRouter,
} from '@angular/router';
import { BehaviorSubject, of, throwError } from 'rxjs';
import { AuthService } from '../../../../core/auth/auth.service';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { AnonymousReactionService } from '../../../../core/privacy/anonymous-reaction.service';
import { SeoService } from '../../../../core/seo/seo.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { NoteDetail, NoteList, NoteStats, NoteTree } from '../../models/notes.model';
import { NotesService } from '../../services/notes.service';
import { NotesPageComponent } from './notes-page.component';

describe('NotesPageComponent', () => {
  let fixture: ComponentFixture<NotesPageComponent>;
  let paramMap: BehaviorSubject<ParamMap>;
  let queryParamMap: BehaviorSubject<ParamMap>;
  let notesService: {
    getPublicTags: jest.Mock;
    getAdminTags: jest.Mock;
    getPublicTree: jest.Mock;
    getAdminTree: jest.Mock;
    getPublicNote: jest.Mock;
    getAdminNote: jest.Mock;
    getPublicNotes: jest.Mock;
    getAdminNotes: jest.Mock;
    trackPublicView: jest.Mock;
    trackPublicEngagedView: jest.Mock;
    setPublicReaction: jest.Mock;
    getAdminStats: jest.Mock;
  };
  let anonymousReactionService: {
    getOrCreateClientToken: jest.Mock;
    getReaction: jest.Mock;
    setReaction: jest.Mock;
  };
  let seoService: {
    setTranslatedMeta: jest.Mock;
    setMeta: jest.Mock;
  };
  let router: { navigate: jest.Mock };
  let canManageContent: boolean;

  beforeEach(async () => {
    canManageContent = false;
    paramMap = new BehaviorSubject(convertToParamMap({ slug: 'typed-notes' }));
    queryParamMap = new BehaviorSubject(convertToParamMap({}));
    notesService = {
      getPublicTags: jest.fn().mockReturnValue(of([])),
      getAdminTags: jest.fn().mockReturnValue(of([])),
      getPublicTree: jest.fn().mockReturnValue(of({ folders: [] } satisfies NoteTree)),
      getAdminTree: jest.fn().mockReturnValue(of({ folders: [] } satisfies NoteTree)),
      getPublicNote: jest.fn().mockReturnValue(of(noteDetail())),
      getAdminNote: jest.fn().mockReturnValue(of(noteDetail())),
      getPublicNotes: jest
        .fn()
        .mockReturnValue(of({ notes: [], totalCount: 0, totalPages: 0 } satisfies NoteList)),
      getAdminNotes: jest
        .fn()
        .mockReturnValue(of({ notes: [], totalCount: 0, totalPages: 0 } satisfies NoteList)),
      trackPublicView: jest.fn().mockReturnValue(of(undefined)),
      trackPublicEngagedView: jest.fn().mockReturnValue(of(undefined)),
      setPublicReaction: jest.fn().mockReturnValue(of(undefined)),
      getAdminStats: jest.fn().mockReturnValue(of(noteStats())),
    };
    anonymousReactionService = {
      getOrCreateClientToken: jest.fn().mockReturnValue('client-token'),
      getReaction: jest.fn().mockReturnValue(null),
      setReaction: jest.fn(),
    };
    seoService = {
      setTranslatedMeta: jest.fn(),
      setMeta: jest.fn(),
    };
    router = { navigate: jest.fn() };

    await TestBed.configureTestingModule({
      imports: [NotesPageComponent],
      providers: [
        provideRouter([]),
        { provide: NotesService, useValue: notesService },
        { provide: AuthService, useValue: { canManageContent: () => canManageContent } },
        { provide: SeoService, useValue: seoService },
        provideI18nTesting(),
        {
          provide: NotificationService,
          useValue: { success: jest.fn(), error: jest.fn() },
        },
        { provide: AnonymousReactionService, useValue: anonymousReactionService },
        {
          provide: ActivatedRoute,
          useValue: {
            paramMap: paramMap.asObservable(),
            queryParamMap: queryParamMap.asObservable(),
          },
        },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(NotesPageComponent);
  });

  afterEach(() => {
    setDocumentVisibility('visible');
    jest.restoreAllMocks();
    fixture.destroy();
  });

  it('sends engaged view once after detail stays open for 30 seconds', fakeAsync(() => {
    fixture.detectChanges();
    notesService.trackPublicEngagedView.mockClear();

    fixture.componentInstance.loadDetail('typed-notes');

    tick(30_000);

    expect(notesService.trackPublicEngagedView).toHaveBeenCalledWith('typed-notes', 'ru');

    tick(30_000);

    expect(notesService.trackPublicEngagedView).toHaveBeenCalledTimes(1);
  }));

  it('sets note-specific SEO meta after loading detail', () => {
    fixture.detectChanges();

    expect(seoService.setMeta).toHaveBeenCalledWith({
      title: 'SEO Typed notes RU',
      description:
        'SEO description RU with enough text to be useful for search snippets and social cards.',
      canonicalPath: '/ru/notes/typed-notes',
      ogImage: 'https://example.com/cover.jpg',
      ogType: 'article',
      alternates: [
        { language: 'ru', path: '/ru/notes/typed-notes' },
        { language: 'en', path: '/en/notes/typed-notes' },
      ],
      structuredData: expect.objectContaining({
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        headline: 'SEO Typed notes RU',
      }),
    });
  });

  it('tracks public view for public published detail and ignores tracking failure', () => {
    notesService.trackPublicView.mockReturnValue(throwError(() => new Error('tracking failed')));

    fixture.detectChanges();

    expect(notesService.trackPublicView).toHaveBeenCalledWith('typed-notes', 'ru');
    expect(seoService.setMeta).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'SEO Typed notes RU',
        canonicalPath: '/ru/notes/typed-notes',
      }),
    );
  });

  it('falls back to note title and excerpt when SEO metadata is null', () => {
    notesService.getPublicNote.mockReturnValue(
      of(
        noteDetail({
          metadata: {
            seoTitleRu: null,
            seoTitleEn: null,
            seoDescriptionRu: null,
            seoDescriptionEn: null,
            coverImageUrl: null,
            coverImageAltRu: null,
            coverImageAltEn: null,
          },
        }),
      ),
    );

    fixture.detectChanges();

    expect(seoService.setMeta).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Typed notes',
        description: 'Excerpt',
        canonicalPath: '/ru/notes/typed-notes',
      }),
    );
  });

  it('does not track public view for content manager detail reads', () => {
    canManageContent = true;

    fixture.detectChanges();

    expect(notesService.getAdminNote).toHaveBeenCalledWith('typed-notes', false, 'ru');
    expect(notesService.getPublicNote).not.toHaveBeenCalled();
    expect(notesService.trackPublicView).not.toHaveBeenCalled();
  });

  it('does not track public view for draft detail reads', () => {
    notesService.getPublicNote.mockReturnValue(of(noteDetail({ publishStatus: 'Draft' })));

    fixture.detectChanges();

    expect(notesService.trackPublicView).not.toHaveBeenCalled();
  });

  it('keeps generic translated SEO meta on the notes list route', () => {
    paramMap.next(convertToParamMap({}));
    fixture.detectChanges();

    expect(seoService.setTranslatedMeta).toHaveBeenCalledWith({
      titleKey: 'notes.seo.title',
      descriptionKey: 'notes.seo.description',
      canonicalPath: '/ru/notes',
      alternates: [
        { language: 'ru', path: '/ru/notes' },
        { language: 'en', path: '/en/notes' },
      ],
    });
  });

  it('pauses engaged view timer while document is hidden', fakeAsync(() => {
    fixture.detectChanges();
    notesService.trackPublicEngagedView.mockClear();

    fixture.componentInstance.loadDetail('typed-notes');

    tick(10_000);
    setDocumentVisibility('hidden');
    tick(30_000);

    expect(notesService.trackPublicEngagedView).not.toHaveBeenCalled();

    setDocumentVisibility('visible');
    tick(19_999);

    expect(notesService.trackPublicEngagedView).not.toHaveBeenCalled();

    tick(1);

    expect(notesService.trackPublicEngagedView).toHaveBeenCalledWith('typed-notes', 'ru');
  }));

  it('creates reaction token lazily and persists selected reaction after success', () => {
    fixture.detectChanges();

    fixture.componentInstance.selectReaction('poop');

    expect(anonymousReactionService.getOrCreateClientToken).toHaveBeenCalled();
    expect(notesService.setPublicReaction).toHaveBeenCalledWith(
      'typed-notes',
      {
        reactionKind: 'poop',
        clientToken: 'client-token',
      },
      'ru',
    );
    expect(anonymousReactionService.setReaction).toHaveBeenCalledWith('typed-notes', 'poop');
    fixture.destroy();
  });

  it('does not submit a reaction when no anonymous client token is available', () => {
    anonymousReactionService.getOrCreateClientToken.mockReturnValue(null);
    fixture.detectChanges();

    fixture.componentInstance.selectReaction('poop');

    expect(notesService.setPublicReaction).not.toHaveBeenCalled();
    expect(anonymousReactionService.setReaction).not.toHaveBeenCalled();
    expect(fixture.componentInstance.reactionLoading()).toBe(false);
  });

  it('loads list filters from query params and requests notes with them', () => {
    paramMap.next(convertToParamMap({}));
    queryParamMap.next(
      convertToParamMap({
        page: '2',
        tag: 'python',
        searchQuery: 'postgres search',
        publishedFrom: '2026-01-01',
        publishedTo: '2026-01-31',
      }),
    );

    fixture.detectChanges();

    expect(notesService.getPublicNotes).toHaveBeenCalledWith({
      page: 2,
      pageSize: 10,
      language: 'ru',
      tagSlug: 'python',
      publishedFrom: '2026-01-01',
      publishedTo: '2026-01-31',
      searchQuery: 'postgres search',
    });
  });

  it('uses admin list API with visibility filter for content managers', () => {
    canManageContent = true;
    paramMap.next(convertToParamMap({}));
    queryParamMap.next(convertToParamMap({ tag: 'python' }));

    fixture.detectChanges();

    expect(notesService.getAdminNotes).toHaveBeenCalledWith({
      page: 1,
      pageSize: 10,
      language: 'ru',
      onlyPublished: true,
      tagSlug: 'python',
      publishedFrom: null,
      publishedTo: null,
      searchQuery: null,
    });
    expect(notesService.getPublicNotes).not.toHaveBeenCalled();
  });

  it('renders the side panel toggle to the left of the title as an icon-only control with localized state labels', () => {
    paramMap.next(convertToParamMap({}));
    fixture.detectChanges();

    const title = fixture.nativeElement.querySelector('h1') as HTMLElement;
    const toggle = fixture.nativeElement.querySelector(
      '[data-testid="notes-side-panel-toggle"]',
    ) as HTMLButtonElement;

    expect(toggle.compareDocumentPosition(title) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(toggle.textContent?.trim()).toBe('');
    expect(toggle.getAttribute('aria-label')).toBe('Открыть папки');
    expect(toggle.title).toBe('Открыть папки');

    toggle.click();
    fixture.detectChanges();

    expect(toggle.getAttribute('aria-label')).toBe('Скрыть папки');
    expect(toggle.title).toBe('Скрыть папки');
    expect(toggle.querySelector('[data-testid="notes-side-panel-close-icon"]')).toBeTruthy();
  });

  it('hides folders and list filters on note detail routes', () => {
    fixture.componentInstance.sidePanelOpen.set(true);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="notes-side-panel-toggle"]')).toBe(
      null,
    );
    expect(fixture.nativeElement.querySelector('[data-testid="notes-side-panel"]')).toBe(null);
    expect(fixture.nativeElement.querySelector('[data-testid="notes-filter-form"]')).toBe(null);
    expect(fixture.nativeElement.querySelector('[data-testid="notes-tag-filters"]')).toBe(null);
  });

  it('renders localized date pickers without visible format hints and keeps ISO query params', () => {
    paramMap.next(convertToParamMap({}));
    fixture.detectChanges();

    const from = fixture.nativeElement.querySelector('#notesPublishedFrom') as HTMLInputElement;
    const to = fixture.nativeElement.querySelector('#notesPublishedTo') as HTMLInputElement;

    expect(from.type).toBe('text');
    expect(to.type).toBe('text');
    expect(from.placeholder).toBe('дд/мм/гггг');
    expect(to.placeholder).toBe('дд/мм/гггг');
    expect(fixture.nativeElement.querySelector('[data-testid="date-picker-toggle"]')).toBeTruthy();
    expect(from.title).toBe('');
    expect(to.title).toBe('');
    expect(fixture.nativeElement.querySelector('#notesPublishedFromHint')).toBe(null);
    expect(fixture.nativeElement.querySelector('#notesPublishedToHint')).toBe(null);

    fixture.nativeElement.querySelector('[data-testid="date-picker-toggle"]').click();
    fixture.detectChanges();

    const monthYearToggle = fixture.nativeElement.querySelector(
      '[data-testid="date-picker-month-year-toggle"]',
    ) as HTMLButtonElement | null;
    expect(monthYearToggle?.getAttribute('aria-label')).toBe('Выбрать месяц и год');

    fixture.componentInstance.setPublishedFrom('2026-01-01');
    fixture.componentInstance.setPublishedTo('2026-01-31');
    fixture.componentInstance.applyFilters();

    expect(router.navigate).toHaveBeenCalledWith(['/', 'ru', 'notes'], {
      queryParams: {
        page: 1,
        publishedFrom: '2026-01-01',
        publishedTo: '2026-01-31',
      },
    });

    TestBed.inject(I18nService).switchLanguage('en').subscribe();
    fixture.detectChanges();

    expect(from.value).toBe('01/01/2026');
    expect(to.value).toBe('01/31/2026');
    expect(from.placeholder).toBe('mm/dd/yyyy');
    expect(to.placeholder).toBe('mm/dd/yyyy');
  });

  it('wraps the statistics panel in an animated shell when visible', () => {
    canManageContent = true;
    paramMap.next(convertToParamMap({}));
    fixture.detectChanges();

    fixture.componentInstance.toggleStats();
    fixture.detectChanges();

    const shell = fixture.nativeElement.querySelector(
      '[data-testid="notes-stats-panel-shell"]',
    ) as HTMLElement;
    expect(shell).toBeTruthy();
    expect(shell.classList).toContain('notes-stats-panel-shell');
  });

  it('reloads localized content when language changes', () => {
    paramMap.next(convertToParamMap({}));
    fixture.detectChanges();
    notesService.getPublicNotes.mockClear();
    notesService.getPublicTags.mockClear();
    notesService.getPublicTree.mockClear();

    TestBed.inject(I18nService).switchLanguage('en').subscribe();
    fixture.detectChanges();

    expect(notesService.getPublicTags).toHaveBeenCalledWith('en');
    expect(notesService.getPublicTree).toHaveBeenCalledWith('en');
    expect(notesService.getPublicNotes).toHaveBeenCalledWith({
      page: 1,
      pageSize: 10,
      language: 'en',
      tagSlug: null,
      publishedFrom: null,
      publishedTo: null,
      searchQuery: null,
    });
  });

  it('makes the published only switch green when enabled for content managers', () => {
    canManageContent = true;
    paramMap.next(convertToParamMap({}));
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('#notesOnlyPublishedToggle')?.classList).toContain(
      'text-bg-success',
    );
  });

  it('applies list filters through query params without fetching on input changes', () => {
    paramMap.next(convertToParamMap({}));
    fixture.detectChanges();
    notesService.getPublicNotes.mockClear();

    fixture.componentInstance.setSearchQuery('  postgres  ');
    fixture.componentInstance.setPublishedFrom('2026-01-01');
    fixture.componentInstance.setPublishedTo('2026-01-31');
    fixture.componentInstance.applyFilters();

    expect(notesService.getPublicNotes).not.toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/', 'ru', 'notes'], {
      queryParams: {
        page: 1,
        searchQuery: 'postgres',
        publishedFrom: '2026-01-01',
        publishedTo: '2026-01-31',
      },
    });
  });

  it('preserves list filters while paginating', () => {
    paramMap.next(convertToParamMap({}));
    queryParamMap.next(
      convertToParamMap({
        tag: 'python',
        searchQuery: 'postgres',
        publishedFrom: '2026-01-01',
        publishedTo: '2026-01-31',
      }),
    );
    fixture.detectChanges();

    fixture.componentInstance.changePage(3);

    expect(router.navigate).toHaveBeenCalledWith(['/', 'ru', 'notes'], {
      queryParams: {
        page: 3,
        tag: 'python',
        searchQuery: 'postgres',
        publishedFrom: '2026-01-01',
        publishedTo: '2026-01-31',
      },
    });
  });

  it('clears tag, search, and date filters together', () => {
    paramMap.next(convertToParamMap({}));
    queryParamMap.next(
      convertToParamMap({
        tag: 'python',
        searchQuery: 'postgres',
        publishedFrom: '2026-01-01',
        publishedTo: '2026-01-31',
      }),
    );
    fixture.detectChanges();

    fixture.componentInstance.clearListFilters();

    expect(router.navigate).toHaveBeenCalledWith(['/', 'ru', 'notes'], {
      queryParams: { page: 1 },
    });
  });
});

function noteDetail(overrides: Partial<NoteDetail> = {}): NoteDetail {
  return {
    id: '00000000-0000-0000-0000-000000000001',
    title: 'Typed notes',
    slug: 'typed-notes',
    folder: 'Engineering',
    authorUsername: 'admin',
    publishedAt: '2026-01-02T03:04:05+00:00',
    publishStatus: 'Published',
    createdAt: '2026-01-01T03:04:05+00:00',
    updatedAt: '2026-01-03T03:04:05+00:00',
    excerpt: 'Excerpt',
    content: '# Content',
    metadata: {
      seoTitleRu: 'SEO Typed notes RU',
      seoTitleEn: 'SEO Typed notes EN',
      seoDescriptionRu:
        'SEO description RU with enough text to be useful for search snippets and social cards.',
      seoDescriptionEn:
        'SEO description EN with enough text to be useful for search snippets and social cards.',
      coverImageUrl: 'https://example.com/cover.jpg',
      coverImageAltRu: 'Cover image RU',
      coverImageAltEn: 'Cover image EN',
    },
    viewCount: 1,
    reactionCounts: { heart: 0, fire: 0, thinking: 0, neutral: 0, poop: 0 },
    tags: [],
    translations: {
      ru: { title: 'Typed notes', content: '# Content', folder: 'Engineering' },
      en: { title: 'Typed notes', content: '# Content', folder: 'Engineering' },
    },
    ...overrides,
  };
}

function setDocumentVisibility(visibilityState: DocumentVisibilityState): void {
  Object.defineProperty(document, 'visibilityState', {
    configurable: true,
    value: visibilityState,
  });
}

function noteStats(): NoteStats {
  return {
    dateFrom: '2026-01-01',
    dateTo: '2026-01-31',
    totals: { viewCount: 0, engagedViewCount: 0, reactionCount: 0 },
    notes: [],
    daily: [],
  };
}
