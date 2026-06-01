import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import {
  ActivatedRoute,
  ParamMap,
  Router,
  convertToParamMap,
  provideRouter,
} from '@angular/router';
import { BehaviorSubject, of } from 'rxjs';
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
    getTags: jest.Mock;
    getTree: jest.Mock;
    getNote: jest.Mock;
    getNotes: jest.Mock;
    trackEngagedView: jest.Mock;
    setReaction: jest.Mock;
    getStats: jest.Mock;
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

  beforeEach(async () => {
    paramMap = new BehaviorSubject(convertToParamMap({ slug: 'typed-notes' }));
    queryParamMap = new BehaviorSubject(convertToParamMap({}));
    notesService = {
      getTags: jest.fn().mockReturnValue(of([])),
      getTree: jest.fn().mockReturnValue(of({ folders: [] } satisfies NoteTree)),
      getNote: jest.fn().mockReturnValue(of(noteDetail())),
      getNotes: jest
        .fn()
        .mockReturnValue(of({ notes: [], totalCount: 0, totalPages: 0 } satisfies NoteList)),
      trackEngagedView: jest.fn().mockReturnValue(of(undefined)),
      setReaction: jest.fn().mockReturnValue(of(undefined)),
      getStats: jest.fn().mockReturnValue(of(noteStats())),
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
        { provide: AuthService, useValue: { isAdmin: () => false } },
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
    notesService.trackEngagedView.mockClear();

    fixture.componentInstance.loadDetail('typed-notes');

    tick(30_000);

    expect(notesService.trackEngagedView).toHaveBeenCalledWith('typed-notes', 'ru');

    tick(30_000);

    expect(notesService.trackEngagedView).toHaveBeenCalledTimes(1);
  }));

  it('sets note-specific SEO meta after loading detail', () => {
    fixture.detectChanges();

    expect(seoService.setMeta).toHaveBeenCalledWith({
      title: 'Typed notes',
      description: 'Excerpt',
      canonicalPath: '/notes/typed-notes',
    });
  });

  it('keeps generic translated SEO meta on the notes list route', () => {
    paramMap.next(convertToParamMap({}));
    fixture.detectChanges();

    expect(seoService.setTranslatedMeta).toHaveBeenCalledWith({
      titleKey: 'notes.seo.title',
      descriptionKey: 'notes.seo.description',
      canonicalPath: '/notes',
    });
  });

  it('pauses engaged view timer while document is hidden', fakeAsync(() => {
    fixture.detectChanges();
    notesService.trackEngagedView.mockClear();

    fixture.componentInstance.loadDetail('typed-notes');

    tick(10_000);
    setDocumentVisibility('hidden');
    tick(30_000);

    expect(notesService.trackEngagedView).not.toHaveBeenCalled();

    setDocumentVisibility('visible');
    tick(19_999);

    expect(notesService.trackEngagedView).not.toHaveBeenCalled();

    tick(1);

    expect(notesService.trackEngagedView).toHaveBeenCalledWith('typed-notes', 'ru');
  }));

  it('creates reaction token lazily and persists selected reaction after success', () => {
    fixture.detectChanges();

    fixture.componentInstance.selectReaction('poop');

    expect(anonymousReactionService.getOrCreateClientToken).toHaveBeenCalled();
    expect(notesService.setReaction).toHaveBeenCalledWith(
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

    expect(notesService.getNotes).toHaveBeenCalledWith({
      page: 2,
      pageSize: 10,
      language: 'ru',
      onlyPublished: true,
      tagSlug: 'python',
      publishedFrom: '2026-01-01',
      publishedTo: '2026-01-31',
      searchQuery: 'postgres search',
    });
  });

  it('reloads localized content when language changes', () => {
    paramMap.next(convertToParamMap({}));
    fixture.detectChanges();
    notesService.getNotes.mockClear();
    notesService.getTags.mockClear();
    notesService.getTree.mockClear();

    TestBed.inject(I18nService).switchLanguage('en').subscribe();
    fixture.detectChanges();

    expect(notesService.getTags).toHaveBeenCalledWith(false, 'en');
    expect(notesService.getTree).toHaveBeenCalledWith('en');
    expect(notesService.getNotes).toHaveBeenCalledWith({
      page: 1,
      pageSize: 10,
      language: 'en',
      onlyPublished: true,
      tagSlug: null,
      publishedFrom: null,
      publishedTo: null,
      searchQuery: null,
    });
  });

  it('applies list filters through query params without fetching on input changes', () => {
    paramMap.next(convertToParamMap({}));
    fixture.detectChanges();
    notesService.getNotes.mockClear();

    fixture.componentInstance.setSearchQuery('  postgres  ');
    fixture.componentInstance.setPublishedFrom('2026-01-01');
    fixture.componentInstance.setPublishedTo('2026-01-31');
    fixture.componentInstance.applyFilters();

    expect(notesService.getNotes).not.toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/notes'], {
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

    expect(router.navigate).toHaveBeenCalledWith(['/notes'], {
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

    expect(router.navigate).toHaveBeenCalledWith(['/notes'], {
      queryParams: { page: 1 },
    });
  });
});

function noteDetail(): NoteDetail {
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
    viewCount: 1,
    reactionCounts: { heart: 0, fire: 0, thinking: 0, neutral: 0, poop: 0 },
    tags: [],
    translations: {
      ru: { title: 'Typed notes', content: '# Content', folder: 'Engineering' },
      en: { title: 'Typed notes', content: '# Content', folder: 'Engineering' },
    },
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
