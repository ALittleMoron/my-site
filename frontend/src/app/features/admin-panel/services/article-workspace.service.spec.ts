import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ApiClient } from '../../../core/http/api-client.service';
import { AdminArticlePayload, AdminArticleTagPayload } from '../models/article-workspace.model';
import { ArticleWorkspaceService } from './article-workspace.service';

const ARTICLE_ID = '00000000000000000000000000000001';
const TAG_ID = '00000000000000000000000000000002';

describe('ArticleWorkspaceService', () => {
  let service: ArticleWorkspaceService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ArticleWorkspaceService,
        ApiClient,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(ArticleWorkspaceService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('loads admin articles with explicit visibility and public stats', () => {
    let firstTitle = '';

    service
      .listArticles({
        page: 2,
        pageSize: 20,
        language: 'en',
        onlyPublished: false,
        tagSlug: 'python',
        publishedFrom: '2026-01-01',
        publishedTo: '2026-01-31',
        searchQuery: 'postgres',
      })
      .subscribe((list) => {
        firstTitle = list.articles[0].title;
      });

    const listReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles'));
    expect(listReq.request.method).toBe('GET');
    expect(listReq.request.params.get('page')).toBe('2');
    expect(listReq.request.params.get('pageSize')).toBe('20');
    expect(listReq.request.params.get('language')).toBe('en');
    expect(listReq.request.params.get('onlyPublished')).toBe('false');
    expect(listReq.request.params.get('tagSlug')).toBe('python');
    expect(listReq.request.params.get('publishedFrom')).toBe('2026-01-01');
    expect(listReq.request.params.get('publishedTo')).toBe('2026-01-31');
    expect(listReq.request.params.get('searchQuery')).toBe('postgres');
    listReq.flush({
      totalCount: 1,
      totalPages: 1,
      articles: [articleSummaryDto()],
    });

    const statsReq = httpMock.expectOne((r) => r.url.endsWith('/api/articles/public-stats'));
    expect(statsReq.request.method).toBe('GET');
    expect(statsReq.request.params.getAll('articleIds')).toEqual([ARTICLE_ID]);
    statsReq.flush({
      stats: [
        {
          articleId: ARTICLE_ID,
          viewCount: 7,
          reactionCounts: { heart: 1, fire: 0, thinking: 0, neutral: 0, poop: 0 },
        },
      ],
    });

    expect(firstTitle).toBe('Typed articles');
  });

  it('creates, updates, publishes, unpublishes, and deletes through admin endpoints', () => {
    service.createArticle(articlePayload(), 'ru').subscribe();
    const createReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles'));
    expect(createReq.request.method).toBe('POST');
    expect(createReq.request.params.get('language')).toBe('ru');
    createReq.flush(articleDetailDto());
    httpMock
      .expectOne((r) => r.url.endsWith('/api/articles/public-stats'))
      .flush({
        stats: [publicStatsDto()],
      });

    service.updateArticle('old-slug', articlePayload(), 'en').subscribe();
    const updateReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/articles/detail/old-slug'),
    );
    expect(updateReq.request.method).toBe('PUT');
    expect(updateReq.request.params.get('language')).toBe('en');
    updateReq.flush(articleDetailDto());
    httpMock
      .expectOne((r) => r.url.endsWith('/api/articles/public-stats'))
      .flush({
        stats: [publicStatsDto()],
      });

    service.publishArticle('typed-articles').subscribe();
    const publishReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/articles/detail/typed-articles/set-published'),
    );
    expect(publishReq.request.method).toBe('POST');
    publishReq.flush(null);

    service.unpublishArticle('typed-articles').subscribe();
    const unpublishReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/articles/detail/typed-articles/set-draft'),
    );
    expect(unpublishReq.request.method).toBe('POST');
    unpublishReq.flush(null);

    service.deleteArticle('typed-articles').subscribe();
    const deleteReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/articles/detail/typed-articles'),
    );
    expect(deleteReq.request.method).toBe('DELETE');
    deleteReq.flush(null);
  });

  it('loads admin detail and tree through admin endpoints', () => {
    service.getArticle('typed-articles', 'en').subscribe();

    const detailReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/articles/detail/typed-articles'),
    );
    expect(detailReq.request.method).toBe('GET');
    expect(detailReq.request.params.get('language')).toBe('en');
    expect(detailReq.request.params.get('onlyPublished')).toBe('false');
    detailReq.flush(articleDetailDto());
    httpMock
      .expectOne((r) => r.url.endsWith('/api/articles/public-stats'))
      .flush({
        stats: [publicStatsDto()],
      });

    service.getTree('ru').subscribe();

    const treeReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles/tree'));
    expect(treeReq.request.method).toBe('GET');
    expect(treeReq.request.params.get('language')).toBe('ru');
    treeReq.flush({ folders: [] });
  });

  it('manages tags through admin endpoints', () => {
    service.getTags(true, 'en').subscribe();

    const listReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles/tags'));
    expect(listReq.request.method).toBe('GET');
    expect(listReq.request.params.get('includeDeleted')).toBe('true');
    expect(listReq.request.params.get('language')).toBe('en');
    listReq.flush({ tags: [] });

    service.searchTags('back', true, 5, 'ru').subscribe();

    const searchReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles/tags/search'));
    expect(searchReq.request.method).toBe('GET');
    expect(searchReq.request.params.get('searchName')).toBe('back');
    expect(searchReq.request.params.get('includeDeleted')).toBe('true');
    expect(searchReq.request.params.get('limit')).toBe('5');
    expect(searchReq.request.params.get('language')).toBe('ru');
    searchReq.flush({ tags: [] });

    service.createTag(tagPayload(), 'ru').subscribe();

    const createReq = httpMock.expectOne((r) => r.url.endsWith('/api/admin/articles/tags'));
    expect(createReq.request.method).toBe('POST');
    expect(createReq.request.params.get('language')).toBe('ru');
    expect(createReq.request.body).toEqual(tagPayload());
    createReq.flush(tagDto());

    service.updateTag(TAG_ID, tagPayload(), 'en').subscribe();

    const updateReq = httpMock.expectOne((r) =>
      r.url.endsWith(`/api/admin/articles/tags/${TAG_ID}`),
    );
    expect(updateReq.request.method).toBe('PUT');
    expect(updateReq.request.params.get('language')).toBe('en');
    expect(updateReq.request.body).toEqual(tagPayload());
    updateReq.flush(tagDto());

    service.deleteTag(TAG_ID).subscribe();

    const deleteReq = httpMock.expectOne((r) =>
      r.url.endsWith(`/api/admin/articles/tags/${TAG_ID}`),
    );
    expect(deleteReq.request.method).toBe('DELETE');
    deleteReq.flush(null);

    service.restoreTag(TAG_ID).subscribe();

    const restoreReq = httpMock.expectOne((r) =>
      r.url.endsWith(`/api/admin/articles/tags/${TAG_ID}/restore`),
    );
    expect(restoreReq.request.method).toBe('POST');
    restoreReq.flush(null);
  });
});

function articleSummaryDto(): unknown {
  return {
    id: ARTICLE_ID,
    title: 'Typed articles',
    slug: 'typed-articles',
    folder: 'Engineering',
    authorUsername: 'admin',
    publishedAt: '2026-01-02T03:04:05+00:00',
    publishStatus: 'Published',
    updatedAt: '2026-01-03T03:04:05+00:00',
    excerpt: 'Excerpt',
    metadata: {
      seoTitleRu: null,
      seoTitleEn: null,
      seoDescriptionRu: null,
      seoDescriptionEn: null,
      coverImageUrl: null,
      coverImageAltRu: null,
      coverImageAltEn: null,
    },
    tags: [],
  };
}

function articleDetailDto(): unknown {
  return {
    ...articleSummaryDto(),
    content: '# Content',
    createdAt: '2026-01-01T03:04:05+00:00',
    translations: {
      ru: { title: 'Typed articles', content: '# Content', folder: 'Engineering' },
      en: { title: 'Typed articles', content: '# Content', folder: 'Engineering' },
    },
  };
}

function publicStatsDto(): unknown {
  return {
    articleId: ARTICLE_ID,
    viewCount: 7,
    reactionCounts: { heart: 1, fire: 0, thinking: 0, neutral: 0, poop: 0 },
  };
}

function articlePayload(): AdminArticlePayload {
  return {
    slug: 'typed-articles',
    publishStatus: 'Draft',
    tagIds: [],
    metadata: {
      seoTitleRu: null,
      seoTitleEn: null,
      seoDescriptionRu: null,
      seoDescriptionEn: null,
      coverImageUrl: null,
      coverImageAltRu: null,
      coverImageAltEn: null,
    },
    translations: {
      ru: { title: 'Typed articles', content: '# Content', folder: 'Engineering' },
      en: { title: 'Typed articles', content: '# Content', folder: 'Engineering' },
    },
  };
}

function tagPayload(): AdminArticleTagPayload {
  return {
    slug: 'backend',
    translations: {
      ru: { name: 'Бэкенд' },
      en: { name: 'Backend' },
    },
  };
}

function tagDto(): unknown {
  return {
    id: TAG_ID,
    name: 'Backend',
    slug: 'backend',
    deletedAt: null,
    translations: {
      ru: { name: 'Бэкенд' },
      en: { name: 'Backend' },
    },
  };
}
