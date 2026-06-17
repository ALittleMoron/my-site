import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import {
  AdminArticleDetail,
  AdminArticleList,
  AdminArticlePayload,
  AdminArticleTag,
  AdminArticleTree,
} from '../../models/article-workspace.model';
import { ArticleWorkspaceService } from '../../services/article-workspace.service';
import { AdminArticlesPageComponent } from './articles-page.component';

describe('AdminArticlesPageComponent', () => {
  let fixture: ComponentFixture<AdminArticlesPageComponent>;
  let service: {
    listArticles: jest.Mock;
    getTags: jest.Mock;
    getTree: jest.Mock;
    getArticle: jest.Mock;
    createArticle: jest.Mock;
    updateArticle: jest.Mock;
    publishArticle: jest.Mock;
    unpublishArticle: jest.Mock;
    deleteArticle: jest.Mock;
  };

  beforeEach(async () => {
    service = {
      listArticles: jest.fn().mockReturnValue(of(articleList())),
      getTags: jest.fn().mockReturnValue(of([] satisfies AdminArticleTag[])),
      getTree: jest.fn().mockReturnValue(of({ folders: [] } satisfies AdminArticleTree)),
      getArticle: jest.fn().mockReturnValue(of(articleDetail())),
      createArticle: jest.fn().mockReturnValue(of(articleDetail())),
      updateArticle: jest.fn().mockReturnValue(of(articleDetail())),
      publishArticle: jest.fn().mockReturnValue(of(undefined)),
      unpublishArticle: jest.fn().mockReturnValue(of(undefined)),
      deleteArticle: jest.fn().mockReturnValue(of(undefined)),
    };

    await TestBed.configureTestingModule({
      imports: [AdminArticlesPageComponent],
      providers: [
        provideRouter([]),
        provideI18nTesting(),
        { provide: ArticleWorkspaceService, useValue: service },
        { provide: NotificationService, useValue: { success: jest.fn(), error: jest.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminArticlesPageComponent);
  });

  it('loads article workspace through admin endpoints and renders authoring controls', () => {
    fixture.detectChanges();

    expect(service.listArticles).toHaveBeenCalledWith({
      page: 1,
      pageSize: 20,
      language: 'ru',
      onlyPublished: false,
      tagSlug: null,
      publishedFrom: null,
      publishedTo: null,
      searchQuery: null,
    });
    expect(fixture.nativeElement.textContent).toContain('Статьи');
    expect(fixture.nativeElement.textContent).toContain('Добавить статью');
    expect(
      fixture.nativeElement.querySelector('[data-testid="admin-articles-only-published"]'),
    ).toBeTruthy();
  });

  it('publishes an article from the admin workspace', () => {
    fixture.detectChanges();

    fixture.componentInstance.publishArticle('typed-articles');

    expect(service.publishArticle).toHaveBeenCalledWith('typed-articles');
    expect(service.listArticles).toHaveBeenCalledTimes(2);
  });

  it('creates an article from the admin workspace', () => {
    const payload = articlePayload();
    fixture.detectChanges();

    fixture.componentInstance.openCreate();
    fixture.componentInstance.saveArticle(payload);

    expect(service.createArticle).toHaveBeenCalledWith(payload, 'ru');
    expect(service.updateArticle).not.toHaveBeenCalled();
    expect(service.listArticles).toHaveBeenCalledTimes(2);
  });

  it('edits an article from the admin workspace', () => {
    const payload = articlePayload();
    fixture.detectChanges();

    fixture.componentInstance.openEdit('typed-articles');
    fixture.componentInstance.saveArticle(payload);

    expect(service.getArticle).toHaveBeenCalledWith('typed-articles', 'ru');
    expect(service.updateArticle).toHaveBeenCalledWith('typed-articles', payload, 'ru');
    expect(service.createArticle).not.toHaveBeenCalled();
    expect(service.listArticles).toHaveBeenCalledTimes(2);
  });

  it('unpublishes and deletes articles from the admin workspace', () => {
    jest.spyOn(window, 'confirm').mockReturnValue(true);
    fixture.detectChanges();

    fixture.componentInstance.unpublishArticle('typed-articles');
    fixture.componentInstance.deleteArticle('typed-articles');

    expect(service.unpublishArticle).toHaveBeenCalledWith('typed-articles');
    expect(service.deleteArticle).toHaveBeenCalledWith('typed-articles');
    expect(service.listArticles).toHaveBeenCalledTimes(3);
  });
});

function articleList(): AdminArticleList {
  return {
    totalCount: 1,
    totalPages: 1,
    articles: [
      {
        id: '00000000-0000-0000-0000-000000000001',
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
        viewCount: 7,
        tags: [],
      },
    ],
  };
}

function articleDetail(): AdminArticleDetail {
  return {
    ...articleList().articles[0],
    content: '# Content',
    createdAt: '2026-01-01T03:04:05+00:00',
    reactionCounts: { heart: 1, fire: 0, thinking: 0, neutral: 0, poop: 0 },
    translations: {
      ru: { title: 'Typed articles', content: '# Content', folder: 'Engineering' },
      en: { title: 'Typed articles', content: '# Content', folder: 'Engineering' },
    },
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
