import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ApiClient } from '../../../core/http/api-client.service';
import { ArticlesService } from './articles.service';

const ARTICLE_ID = '00000000-0000-0000-0000-000000000001';

describe('ArticlesService', () => {
  let service: ArticlesService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ArticlesService, ApiClient, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(ArticlesService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('loads public articles with pagination and public-safe filters', () => {
    let firstTitle: string | undefined;
    let firstViewCount: number | undefined;
    let firstSeoTitle: string | null | undefined;

    service
      .getPublicArticles({
        page: 2,
        pageSize: 10,
        language: 'en',
        tagSlug: 'python',
        publishedFrom: '2026-01-01',
        publishedTo: '2026-01-31',
        searchQuery: 'typed articles',
      })
      .subscribe((list) => {
        firstTitle = list.articles[0].title;
        firstViewCount = list.articles[0].viewCount;
        firstSeoTitle = list.articles[0].metadata.seoTitleEn;
      });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/articles'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('page')).toBe('2');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.params.get('pageSize')).toBe('10');
    expect(req.request.params.has('onlyPublished')).toBe(false);
    expect(req.request.params.get('tagSlug')).toBe('python');
    expect(req.request.params.get('publishedFrom')).toBe('2026-01-01');
    expect(req.request.params.get('publishedTo')).toBe('2026-01-31');
    expect(req.request.params.get('searchQuery')).toBe('typed articles');
    req.flush({
      totalCount: 1,
      totalPages: 1,
      articles: [
        {
          id: ARTICLE_ID,
          title: 'Typed articles',
          content: 'Ignored in list',
          slug: 'typed-articles',
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
    flushPublicStats(httpMock, [{ articleId: ARTICLE_ID, viewCount: 42 }]);

    expect(firstTitle).toBe('Typed articles');
    expect(firstViewCount).toBe(42);
    expect(firstSeoTitle).toBe('SEO Typed articles');
  });

  it('loads admin articles with explicit visibility', () => {
    service
      .getAdminArticles({
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

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('page')).toBe('1');
    expect(req.request.params.get('pageSize')).toBe('10');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.params.get('onlyPublished')).toBe('false');
    req.flush({ totalCount: 0, totalPages: 0, articles: [] });
  });

  it('loads public detail without visibility query params', () => {
    let content: string | undefined;
    let fireCount: number | undefined;
    let seoDescription: string | null | undefined;

    service.getPublicArticle('typed-articles', 'ru').subscribe((article) => {
      content = article.content;
      fireCount = article.reactionCounts.fire;
      seoDescription = article.metadata.seoDescriptionRu;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/articles/detail/typed-articles'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('ru');
    expect(req.request.params.has('onlyPublished')).toBe(false);
    req.flush({
      id: ARTICLE_ID,
      title: 'Typed articles',
      content: '# Markdown',
      slug: 'typed-articles',
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
        ru: { title: 'Типизированные статьи', content: '# Markdown', folder: 'Инженерия' },
        en: { title: 'Typed articles', content: '# Markdown', folder: 'Engineering' },
      },
    });
    flushPublicStats(httpMock, [
      {
        articleId: ARTICLE_ID,
        viewCount: 5,
        reactionCounts: { heart: 1, fire: 2, thinking: 3, neutral: 4, poop: 5 },
      },
    ]);

    expect(content).toBe('# Markdown');
    expect(fireCount).toBe(2);
    expect(seoDescription).toBe('SEO описание');
  });

  it('loads admin detail with explicit visibility', () => {
    service.getAdminArticle('typed-articles', false, 'en').subscribe();

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/articles/detail/typed-articles'),
    );
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.params.get('onlyPublished')).toBe('false');
    req.flush(articleDetailDto());
    flushPublicStats(httpMock, [{ articleId: ARTICLE_ID, viewCount: 0 }]);
  });

  it('tracks engagement and reactions', () => {
    service.trackPublicView('typed-articles', 'ru').subscribe();
    const viewReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/articles/detail/typed-articles/analytics/view'),
    );
    expect(viewReq.request.method).toBe('POST');
    expect(viewReq.request.params.get('language')).toBe('ru');
    viewReq.flush(null);

    service.trackPublicEngagedView('typed-articles', 'ru').subscribe();
    const engagedReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/articles/detail/typed-articles/analytics/engaged-view'),
    );
    expect(engagedReq.request.method).toBe('POST');
    expect(engagedReq.request.params.get('language')).toBe('ru');
    engagedReq.flush(null);

    service
      .setPublicReaction(
        'typed-articles',
        { reactionKind: 'poop', clientToken: 'client-token' },
        'en',
      )
      .subscribe();
    const reactionReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/articles/detail/typed-articles/reaction'),
    );
    expect(reactionReq.request.method).toBe('POST');
    expect(reactionReq.request.params.get('language')).toBe('en');
    expect(reactionReq.request.body).toEqual({
      reactionKind: 'poop',
      clientToken: 'client-token',
    });
    reactionReq.flush(null);
  });

  it('loads admin article statistics', () => {
    let reactionTotal: number | undefined;

    service
      .getAdminStats({ dateFrom: '2026-01-01', dateTo: '2026-01-31', language: 'en' })
      .subscribe((stats) => {
        reactionTotal = stats.totals.reactionCount;
      });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles/stats'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.params.get('dateFrom')).toBe('2026-01-01');
    expect(req.request.params.get('dateTo')).toBe('2026-01-31');
    req.flush({
      dateFrom: '2026-01-01',
      dateTo: '2026-01-31',
      totals: { viewCount: 7, engagedViewCount: 3, reactionCount: 2 },
      articles: [
        {
          articleId: '00000000-0000-0000-0000-000000000001',
          title: 'Typed articles',
          slug: 'typed-articles',
          viewCount: 7,
          engagedViewCount: 3,
          reactionCounts: { heart: 1, fire: 0, thinking: 1, neutral: 0, poop: 0 },
        },
      ],
      daily: [
        {
          articleId: '00000000-0000-0000-0000-000000000001',
          title: 'Typed articles',
          slug: 'typed-articles',
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

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/articles/tree'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('ru');
    req.flush({
      folders: [
        {
          folder: 'Engineering',
          articles: [
            {
              title: 'Typed articles',
              slug: 'typed-articles',
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

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles/tree'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('en');
    req.flush({ folders: [] });
  });

  it('creates and updates articles with editable slug and tags', () => {
    service
      .createAdminArticle(
        {
          slug: 'new-article',
          publishStatus: 'Draft',
          tagIds: [1],
          metadata: metadataDto(),
          translations: {
            ru: { title: 'Новая статья', content: 'Содержимое', folder: 'Входящие' },
            en: { title: 'New article', content: 'Content', folder: 'Inbox' },
          },
        },
        'ru',
      )
      .subscribe();

    const createReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles'));
    expect(createReq.request.method).toBe('POST');
    expect(createReq.request.params.get('language')).toBe('ru');
    expect(createReq.request.body.slug).toBe('new-article');
    expect(createReq.request.body.tagIds).toEqual([1]);
    expect(createReq.request.body.metadata.seoTitleEn).toBe('SEO Typed articles');
    expect(createReq.request.body.translations.en.title).toBe('New article');
    createReq.flush(articleDetailDto());
    flushPublicStats(httpMock, [{ articleId: ARTICLE_ID, viewCount: 0 }]);

    service
      .updateAdminArticle(
        'old-article',
        {
          slug: 'new-article',
          publishStatus: 'Published',
          tagIds: [1, 2],
          metadata: {
            ...metadataDto(),
            seoTitleEn: null,
            coverImageUrl: null,
          },
          translations: {
            ru: { title: 'Новая статья', content: 'Содержимое', folder: 'Входящие' },
            en: { title: 'New article', content: 'Content', folder: 'Inbox' },
          },
        },
        'en',
      )
      .subscribe();

    const updateReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/articles/detail/old-article'),
    );
    expect(updateReq.request.method).toBe('PUT');
    expect(updateReq.request.params.get('language')).toBe('en');
    expect(updateReq.request.body.publishStatus).toBe('Published');
    expect(updateReq.request.body.tagIds).toEqual([1, 2]);
    expect(updateReq.request.body.metadata.seoTitleEn).toBeNull();
    expect(updateReq.request.body.metadata.coverImageUrl).toBeNull();
    updateReq.flush(articleDetailDto());
    flushPublicStats(httpMock, [{ articleId: ARTICLE_ID, viewCount: 0 }]);
  });

  it('calls article publish endpoints', () => {
    service.publishAdminArticle('draft-article').subscribe();
    const publishReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/articles/detail/draft-article/set-published'),
    );
    expect(publishReq.request.method).toBe('POST');
    publishReq.flush(null);

    service.unpublishAdminArticle('published-article').subscribe();
    const unpublishReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/articles/detail/published-article/set-draft'),
    );
    expect(unpublishReq.request.method).toBe('POST');
    unpublishReq.flush(null);
  });

  it('loads public tags without deleted-content controls', () => {
    service.getPublicTags('en').subscribe();

    const listReq = httpMock.expectOne((r) => r.url.endsWith('/api/articles/tags'));
    expect(listReq.request.params.has('includeDeleted')).toBe(false);
    expect(listReq.request.params.get('language')).toBe('en');
    listReq.flush({ tags: [] });
  });

  it('manages tags through admin endpoints', () => {
    service.getAdminTags(true, 'en').subscribe();
    const listReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles/tags'));
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
    const createReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles/tags'));
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
    const updateReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles/tags/1'));
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
    const deleteReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles/tags/1'));
    expect(deleteReq.request.method).toBe('DELETE');
    deleteReq.flush(null);

    service.restoreAdminTag(1).subscribe();
    const restoreReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/articles/tags/1/restore'),
    );
    expect(restoreReq.request.method).toBe('POST');
    restoreReq.flush(null);
  });
});

function articleDetailDto(): unknown {
  return {
    id: ARTICLE_ID,
    title: 'New article',
    content: 'Content',
    slug: 'new-article',
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
      ru: { title: 'Новая статья', content: 'Содержимое', folder: 'Входящие' },
      en: { title: 'New article', content: 'Content', folder: 'Inbox' },
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
    seoTitleRu: 'SEO статья',
    seoTitleEn: 'SEO Typed articles',
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
    articleId: string;
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
  const req = httpMock.expectOne((r) => r.url.endsWith('/api/articles/public-stats'));
  expect(req.request.method).toBe('GET');
  expect(req.request.params.getAll('articleIds')).toEqual(stats.map((item) => item.articleId));
  req.flush({
    stats: stats.map((item) => ({
      articleId: item.articleId,
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
