import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ApiClient } from '../../../core/http/api-client.service';
import { NotesService } from './notes.service';

const NOTE_ID = '00000000-0000-0000-0000-000000000001';

describe('NotesService', () => {
  let service: NotesService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [NotesService, ApiClient, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(NotesService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('loads public notes with pagination and public-safe filters', () => {
    let firstTitle: string | undefined;
    let firstViewCount: number | undefined;
    let firstSeoTitle: string | null | undefined;

    service
      .getPublicNotes({
        page: 2,
        pageSize: 10,
        language: 'en',
        tagSlug: 'python',
        publishedFrom: '2026-01-01',
        publishedTo: '2026-01-31',
        searchQuery: 'typed notes',
      })
      .subscribe((list) => {
        firstTitle = list.notes[0].title;
        firstViewCount = list.notes[0].viewCount;
        firstSeoTitle = list.notes[0].metadata.seoTitleEn;
      });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/notes'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('page')).toBe('2');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.params.get('pageSize')).toBe('10');
    expect(req.request.params.has('onlyPublished')).toBe(false);
    expect(req.request.params.get('tagSlug')).toBe('python');
    expect(req.request.params.get('publishedFrom')).toBe('2026-01-01');
    expect(req.request.params.get('publishedTo')).toBe('2026-01-31');
    expect(req.request.params.get('searchQuery')).toBe('typed notes');
    req.flush({
      totalCount: 1,
      totalPages: 1,
      notes: [
        {
          id: NOTE_ID,
          title: 'Typed notes',
          content: 'Ignored in list',
          slug: 'typed-notes',
          folder: 'Engineering',
          authorUsername: 'admin',
          publishedAt: '2026-01-02T03:04:05+00:00',
          publishStatus: 'Published',
          updatedAt: '2026-01-03T03:04:05+00:00',
          excerpt: 'Excerpt',
          metadata: metadataDto(),
          tags: [
            {
              id: 1,
              name: 'Python',
              slug: 'python',
              deletedAt: null,
              translations: { ru: { name: 'Python' }, en: { name: 'Python' } },
            },
          ],
        },
      ],
    });
    flushPublicStats(httpMock, [{ noteId: NOTE_ID, viewCount: 42 }]);

    expect(firstTitle).toBe('Typed notes');
    expect(firstViewCount).toBe(42);
    expect(firstSeoTitle).toBe('SEO Typed notes');
  });

  it('loads admin notes with explicit visibility', () => {
    service
      .getAdminNotes({
        page: 1,
        pageSize: 10,
        language: 'en',
        onlyPublished: false,
        tagSlug: null,
        publishedFrom: null,
        publishedTo: null,
        searchQuery: null,
      })
      .subscribe();

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('page')).toBe('1');
    expect(req.request.params.get('pageSize')).toBe('10');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.params.get('onlyPublished')).toBe('false');
    req.flush({ totalCount: 0, totalPages: 0, notes: [] });
  });

  it('loads public detail without visibility query params', () => {
    let content: string | undefined;
    let fireCount: number | undefined;
    let seoDescription: string | null | undefined;

    service.getPublicNote('typed-notes', 'ru').subscribe((note) => {
      content = note.content;
      fireCount = note.reactionCounts.fire;
      seoDescription = note.metadata.seoDescriptionRu;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/notes/detail/typed-notes'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('ru');
    expect(req.request.params.has('onlyPublished')).toBe(false);
    req.flush({
      id: NOTE_ID,
      title: 'Typed notes',
      content: '# Markdown',
      slug: 'typed-notes',
      folder: 'Engineering',
      authorUsername: 'admin',
      publishedAt: '2026-01-02T03:04:05+00:00',
      publishStatus: 'Published',
      createdAt: '2026-01-01T03:04:05+00:00',
      updatedAt: '2026-01-03T03:04:05+00:00',
      excerpt: 'Markdown',
      metadata: metadataDto(),
      tags: [],
      translations: {
        ru: { title: 'Типизированные заметки', content: '# Markdown', folder: 'Инженерия' },
        en: { title: 'Typed notes', content: '# Markdown', folder: 'Engineering' },
      },
    });
    flushPublicStats(httpMock, [
      {
        noteId: NOTE_ID,
        viewCount: 5,
        reactionCounts: { heart: 1, fire: 2, thinking: 3, neutral: 4, poop: 5 },
      },
    ]);

    expect(content).toBe('# Markdown');
    expect(fireCount).toBe(2);
    expect(seoDescription).toBe('SEO описание');
  });

  it('loads admin detail with explicit visibility', () => {
    service.getAdminNote('typed-notes', false, 'en').subscribe();

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes/detail/typed-notes'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.params.get('onlyPublished')).toBe('false');
    req.flush(noteDetailDto());
    flushPublicStats(httpMock, [{ noteId: NOTE_ID, viewCount: 0 }]);
  });

  it('tracks engagement and reactions', () => {
    service.trackPublicView('typed-notes', 'ru').subscribe();
    const viewReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/notes/detail/typed-notes/analytics/view'),
    );
    expect(viewReq.request.method).toBe('POST');
    expect(viewReq.request.params.get('language')).toBe('ru');
    viewReq.flush(null);

    service.trackPublicEngagedView('typed-notes', 'ru').subscribe();
    const engagedReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/notes/detail/typed-notes/analytics/engaged-view'),
    );
    expect(engagedReq.request.method).toBe('POST');
    expect(engagedReq.request.params.get('language')).toBe('ru');
    engagedReq.flush(null);

    service
      .setPublicReaction('typed-notes', { reactionKind: 'poop', clientToken: 'client-token' }, 'en')
      .subscribe();
    const reactionReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/notes/detail/typed-notes/reaction'),
    );
    expect(reactionReq.request.method).toBe('POST');
    expect(reactionReq.request.params.get('language')).toBe('en');
    expect(reactionReq.request.body).toEqual({
      reactionKind: 'poop',
      clientToken: 'client-token',
    });
    reactionReq.flush(null);
  });

  it('loads admin note statistics', () => {
    let reactionTotal: number | undefined;

    service
      .getAdminStats({ dateFrom: '2026-01-01', dateTo: '2026-01-31', language: 'en' })
      .subscribe((stats) => {
        reactionTotal = stats.totals.reactionCount;
      });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes/stats'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.params.get('dateFrom')).toBe('2026-01-01');
    expect(req.request.params.get('dateTo')).toBe('2026-01-31');
    req.flush({
      dateFrom: '2026-01-01',
      dateTo: '2026-01-31',
      totals: { viewCount: 7, engagedViewCount: 3, reactionCount: 2 },
      notes: [
        {
          noteId: '00000000-0000-0000-0000-000000000001',
          title: 'Typed notes',
          slug: 'typed-notes',
          viewCount: 7,
          engagedViewCount: 3,
          reactionCounts: { heart: 1, fire: 0, thinking: 1, neutral: 0, poop: 0 },
        },
      ],
      daily: [
        {
          noteId: '00000000-0000-0000-0000-000000000001',
          title: 'Typed notes',
          slug: 'typed-notes',
          date: '2026-01-02',
          sourceCategory: 'Search',
          viewCount: 7,
          engagedViewCount: 3,
        },
      ],
    });

    expect(reactionTotal).toBe(2);
  });

  it('loads tree without tag filters', () => {
    let firstFolder: string | undefined;

    service.getPublicTree('ru').subscribe((tree) => {
      firstFolder = tree.folders[0].folder;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tree'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('ru');
    req.flush({
      folders: [
        {
          folder: 'Engineering',
          notes: [
            {
              title: 'Typed notes',
              slug: 'typed-notes',
              publishStatus: 'Published',
              publishedAt: '2026-01-02T03:04:05+00:00',
              updatedAt: '2026-01-03T03:04:05+00:00',
            },
          ],
        },
      ],
    });

    expect(firstFolder).toBe('Engineering');
  });

  it('loads admin tree from the admin surface', () => {
    service.getAdminTree('en').subscribe();

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes/tree'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('en');
    req.flush({ folders: [] });
  });

  it('creates and updates notes with editable slug and tags', () => {
    service
      .createAdminNote(
        {
          slug: 'new-note',
          publishStatus: 'Draft',
          tagIds: [1],
          metadata: metadataDto(),
          translations: {
            ru: { title: 'Новая заметка', content: 'Содержимое', folder: 'Входящие' },
            en: { title: 'New note', content: 'Content', folder: 'Inbox' },
          },
        },
        'ru',
      )
      .subscribe();

    const createReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes'));
    expect(createReq.request.method).toBe('POST');
    expect(createReq.request.params.get('language')).toBe('ru');
    expect(createReq.request.body.slug).toBe('new-note');
    expect(createReq.request.body.tagIds).toEqual([1]);
    expect(createReq.request.body.metadata.seoTitleEn).toBe('SEO Typed notes');
    expect(createReq.request.body.translations.en.title).toBe('New note');
    createReq.flush(noteDetailDto());
    flushPublicStats(httpMock, [{ noteId: NOTE_ID, viewCount: 0 }]);

    service
      .updateAdminNote(
        'old-note',
        {
          slug: 'new-note',
          publishStatus: 'Published',
          tagIds: [1, 2],
          metadata: {
            ...metadataDto(),
            seoTitleEn: null,
            coverImageUrl: null,
          },
          translations: {
            ru: { title: 'Новая заметка', content: 'Содержимое', folder: 'Входящие' },
            en: { title: 'New note', content: 'Content', folder: 'Inbox' },
          },
        },
        'en',
      )
      .subscribe();

    const updateReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes/detail/old-note'));
    expect(updateReq.request.method).toBe('PUT');
    expect(updateReq.request.params.get('language')).toBe('en');
    expect(updateReq.request.body.publishStatus).toBe('Published');
    expect(updateReq.request.body.tagIds).toEqual([1, 2]);
    expect(updateReq.request.body.metadata.seoTitleEn).toBeNull();
    expect(updateReq.request.body.metadata.coverImageUrl).toBeNull();
    updateReq.flush(noteDetailDto());
    flushPublicStats(httpMock, [{ noteId: NOTE_ID, viewCount: 0 }]);
  });

  it('calls note publish endpoints', () => {
    service.publishAdminNote('draft-note').subscribe();
    const publishReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/notes/detail/draft-note/set-published'),
    );
    expect(publishReq.request.method).toBe('POST');
    publishReq.flush(null);

    service.unpublishAdminNote('published-note').subscribe();
    const unpublishReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/notes/detail/published-note/set-draft'),
    );
    expect(unpublishReq.request.method).toBe('POST');
    unpublishReq.flush(null);
  });

  it('loads public tags without deleted-content controls', () => {
    service.getPublicTags('en').subscribe();

    const listReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags'));
    expect(listReq.request.params.has('includeDeleted')).toBe(false);
    expect(listReq.request.params.get('language')).toBe('en');
    listReq.flush({ tags: [] });
  });

  it('manages tags through admin endpoints', () => {
    service.getAdminTags(true, 'en').subscribe();
    const listReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes/tags'));
    expect(listReq.request.params.get('includeDeleted')).toBe('true');
    expect(listReq.request.params.get('language')).toBe('en');
    listReq.flush({ tags: [] });

    service
      .createAdminTag(
        {
          slug: 'backend',
          translations: { ru: { name: 'Бэкенд' }, en: { name: 'Backend' } },
        },
        'ru',
      )
      .subscribe();
    const createReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes/tags'));
    expect(createReq.request.method).toBe('POST');
    expect(createReq.request.params.get('language')).toBe('ru');
    expect(createReq.request.body).toEqual({
      slug: 'backend',
      translations: { ru: { name: 'Бэкенд' }, en: { name: 'Backend' } },
    });
    createReq.flush({
      id: 1,
      name: 'Backend',
      slug: 'backend',
      deletedAt: null,
      translations: { ru: { name: 'Бэкенд' }, en: { name: 'Backend' } },
    });

    service
      .updateAdminTag(
        1,
        {
          slug: 'architecture',
          translations: { ru: { name: 'Архитектура' }, en: { name: 'Architecture' } },
        },
        'en',
      )
      .subscribe();
    const updateReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes/tags/1'));
    expect(updateReq.request.method).toBe('PUT');
    expect(updateReq.request.params.get('language')).toBe('en');
    updateReq.flush({
      id: 1,
      name: 'Architecture',
      slug: 'architecture',
      deletedAt: null,
      translations: { ru: { name: 'Архитектура' }, en: { name: 'Architecture' } },
    });

    service.deleteAdminTag(1).subscribe();
    const deleteReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes/tags/1'));
    expect(deleteReq.request.method).toBe('DELETE');
    deleteReq.flush(null);

    service.restoreAdminTag(1).subscribe();
    const restoreReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/notes/tags/1/restore'));
    expect(restoreReq.request.method).toBe('POST');
    restoreReq.flush(null);
  });
});

function noteDetailDto(): unknown {
  return {
    id: NOTE_ID,
    title: 'New note',
    content: 'Content',
    slug: 'new-note',
    folder: 'Inbox',
    authorUsername: 'admin',
    publishedAt: null,
    publishStatus: 'Draft',
    createdAt: '2026-01-01T03:04:05+00:00',
    updatedAt: '2026-01-03T03:04:05+00:00',
    excerpt: 'Content',
    metadata: metadataDto(),
    tags: [],
    translations: {
      ru: { title: 'Новая заметка', content: 'Содержимое', folder: 'Входящие' },
      en: { title: 'New note', content: 'Content', folder: 'Inbox' },
    },
  };
}

function metadataDto(): {
  seoTitleRu: string | null;
  seoTitleEn: string | null;
  seoDescriptionRu: string | null;
  seoDescriptionEn: string | null;
  coverImageUrl: string | null;
  coverImageAltRu: string | null;
  coverImageAltEn: string | null;
} {
  return {
    seoTitleRu: 'SEO заметка',
    seoTitleEn: 'SEO Typed notes',
    seoDescriptionRu: 'SEO описание',
    seoDescriptionEn: 'SEO description',
    coverImageUrl: 'https://example.com/cover.jpg',
    coverImageAltRu: 'Обложка',
    coverImageAltEn: 'Cover',
  };
}

function flushPublicStats(
  httpMock: HttpTestingController,
  stats: {
    noteId: string;
    viewCount: number;
    reactionCounts?: {
      heart: number;
      fire: number;
      thinking: number;
      neutral: number;
      poop: number;
    };
  }[],
): void {
  const req = httpMock.expectOne((r) => r.url.endsWith('/api/notes/public-stats'));
  expect(req.request.method).toBe('GET');
  expect(req.request.params.getAll('noteIds')).toEqual(stats.map((item) => item.noteId));
  req.flush({
    stats: stats.map((item) => ({
      noteId: item.noteId,
      viewCount: item.viewCount,
      reactionCounts: item.reactionCounts ?? {
        heart: 0,
        fire: 0,
        thinking: 0,
        neutral: 0,
        poop: 0,
      },
    })),
  });
}
