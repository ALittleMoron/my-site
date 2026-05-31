import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ApiClient } from '../../../core/http/api-client.service';
import { NotesService } from './notes.service';

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

  it('loads notes with pagination, visibility, and tag filters', () => {
    let firstTitle: string | undefined;
    let firstViewCount: number | undefined;

    service
      .getNotes({
        page: 2,
        pageSize: 10,
        language: 'en',
        onlyPublished: false,
        tagSlug: 'python',
        publishedFrom: '2026-01-01',
        publishedTo: '2026-01-31',
        searchQuery: 'typed notes',
      })
      .subscribe((list) => {
        firstTitle = list.notes[0].title;
        firstViewCount = list.notes[0].viewCount;
      });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/notes'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('page')).toBe('2');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.params.get('pageSize')).toBe('10');
    expect(req.request.params.get('onlyPublished')).toBe('false');
    expect(req.request.params.get('tagSlug')).toBe('python');
    expect(req.request.params.get('publishedFrom')).toBe('2026-01-01');
    expect(req.request.params.get('publishedTo')).toBe('2026-01-31');
    expect(req.request.params.get('searchQuery')).toBe('typed notes');
    req.flush({
      totalCount: 1,
      totalPages: 1,
      notes: [
        {
          id: '00000000-0000-0000-0000-000000000001',
          title: 'Typed notes',
          content: 'Ignored in list',
          slug: 'typed-notes',
          folder: 'Engineering',
          authorUsername: 'admin',
          publishedAt: '2026-01-02T03:04:05+00:00',
          publishStatus: 'Published',
          updatedAt: '2026-01-03T03:04:05+00:00',
          excerpt: 'Excerpt',
          viewCount: 42,
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

    expect(firstTitle).toBe('Typed notes');
    expect(firstViewCount).toBe(42);
  });

  it('loads detail with explicit visibility', () => {
    let content: string | undefined;
    let fireCount: number | undefined;

    service.getNote('typed-notes', true, 'ru').subscribe((note) => {
      content = note.content;
      fireCount = note.reactionCounts.fire;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/notes/detail/typed-notes'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('ru');
    expect(req.request.params.get('onlyPublished')).toBe('true');
    req.flush({
      id: '00000000-0000-0000-0000-000000000001',
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
      viewCount: 5,
      reactionCounts: { heart: 1, fire: 2, thinking: 3, neutral: 4, poop: 5 },
      tags: [],
    });

    expect(content).toBe('# Markdown');
    expect(fireCount).toBe(2);
  });

  it('tracks engagement and reactions', () => {
    service.trackEngagedView('typed-notes', 'ru').subscribe();
    const engagedReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/notes/detail/typed-notes/analytics/engaged-view'),
    );
    expect(engagedReq.request.method).toBe('POST');
    expect(engagedReq.request.params.get('language')).toBe('ru');
    engagedReq.flush(null);

    service
      .setReaction('typed-notes', { reactionKind: 'poop', clientToken: 'client-token' }, 'en')
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
      .getStats({ dateFrom: '2026-01-01', dateTo: '2026-01-31', language: 'en' })
      .subscribe((stats) => {
        reactionTotal = stats.totals.reactionCount;
      });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/notes/stats'));
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

    service.getTree('ru').subscribe((tree) => {
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

  it('creates and updates notes with editable slug and tags', () => {
    service
      .createNote(
        {
          slug: 'new-note',
          publishStatus: 'Draft',
          tagIds: [1],
          translations: {
            ru: { title: 'Новая заметка', content: 'Содержимое', folder: 'Входящие' },
            en: { title: 'New note', content: 'Content', folder: 'Inbox' },
          },
        },
        'ru',
      )
      .subscribe();

    const createReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes'));
    expect(createReq.request.method).toBe('POST');
    expect(createReq.request.params.get('language')).toBe('ru');
    expect(createReq.request.body.slug).toBe('new-note');
    expect(createReq.request.body.tagIds).toEqual([1]);
    expect(createReq.request.body.translations.en.title).toBe('New note');
    createReq.flush(noteDetailDto());

    service
      .updateNote(
        'old-note',
        {
          slug: 'new-note',
          publishStatus: 'Published',
          tagIds: [1, 2],
          translations: {
            ru: { title: 'Новая заметка', content: 'Содержимое', folder: 'Входящие' },
            en: { title: 'New note', content: 'Content', folder: 'Inbox' },
          },
        },
        'en',
      )
      .subscribe();

    const updateReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/detail/old-note'));
    expect(updateReq.request.method).toBe('PUT');
    expect(updateReq.request.params.get('language')).toBe('en');
    expect(updateReq.request.body.publishStatus).toBe('Published');
    expect(updateReq.request.body.tagIds).toEqual([1, 2]);
    updateReq.flush(noteDetailDto());
  });

  it('calls note publish endpoints', () => {
    service.publishNote('draft-note').subscribe();
    const publishReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/notes/detail/draft-note/set-published'),
    );
    expect(publishReq.request.method).toBe('POST');
    publishReq.flush(null);

    service.unpublishNote('published-note').subscribe();
    const unpublishReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/notes/detail/published-note/set-draft'),
    );
    expect(unpublishReq.request.method).toBe('POST');
    unpublishReq.flush(null);
  });

  it('manages tags', () => {
    service.getTags(true, 'en').subscribe();
    const listReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags'));
    expect(listReq.request.params.get('includeDeleted')).toBe('true');
    expect(listReq.request.params.get('language')).toBe('en');
    listReq.flush({ tags: [] });

    service
      .createTag(
        {
          slug: 'backend',
          translations: { ru: { name: 'Бэкенд' }, en: { name: 'Backend' } },
        },
        'ru',
      )
      .subscribe();
    const createReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags'));
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
      .updateTag(
        1,
        {
          slug: 'architecture',
          translations: { ru: { name: 'Архитектура' }, en: { name: 'Architecture' } },
        },
        'en',
      )
      .subscribe();
    const updateReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags/1'));
    expect(updateReq.request.method).toBe('PUT');
    expect(updateReq.request.params.get('language')).toBe('en');
    updateReq.flush({
      id: 1,
      name: 'Architecture',
      slug: 'architecture',
      deletedAt: null,
      translations: { ru: { name: 'Архитектура' }, en: { name: 'Architecture' } },
    });

    service.deleteTag(1).subscribe();
    const deleteReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags/1'));
    expect(deleteReq.request.method).toBe('DELETE');
    deleteReq.flush(null);

    service.restoreTag(1).subscribe();
    const restoreReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags/1/restore'));
    expect(restoreReq.request.method).toBe('POST');
    restoreReq.flush(null);
  });
});

function noteDetailDto(): unknown {
  return {
    id: '00000000-0000-0000-0000-000000000001',
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
    viewCount: 0,
    reactionCounts: { heart: 0, fire: 0, thinking: 0, neutral: 0, poop: 0 },
    tags: [],
    translations: {
      ru: { title: 'Новая заметка', content: 'Содержимое', folder: 'Входящие' },
      en: { title: 'New note', content: 'Content', folder: 'Inbox' },
    },
  };
}
