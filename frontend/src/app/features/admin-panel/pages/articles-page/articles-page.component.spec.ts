import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
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
    getFolders: jest.Mock;
    createFolder: jest.Mock;
    updateFolderPriorities: jest.Mock;
    getTree: jest.Mock;
    getArticle: jest.Mock;
    createArticle: jest.Mock;
    updateArticle: jest.Mock;
    publishArticle: jest.Mock;
    unpublishArticle: jest.Mock;
    deleteArticle: jest.Mock;
  };
  let router: Router;

  beforeEach(async () => {
    service = {
      listArticles: jest.fn().mockReturnValue(of(articleList())),
      getTags: jest.fn().mockReturnValue(of([] satisfies AdminArticleTag[])),
      getFolders: jest.fn().mockReturnValue(of([])),
      createFolder: jest.fn().mockReturnValue(of(null)),
      updateFolderPriorities: jest.fn().mockReturnValue(of(undefined)),
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
    router = TestBed.inject(Router);
    jest.spyOn(router, 'navigate').mockResolvedValue(true);
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

  it('routes the row edit action to the article detail page from the actions dropdown', () => {
    fixture.detectChanges();

    const toggle = fixture.nativeElement.querySelector(
      '[data-testid="article-actions-typed-articles-toggle"]',
    ) as HTMLButtonElement | null;
    expect(toggle).not.toBeNull();
    toggle?.click();
    fixture.detectChanges();
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="article-actions-typed-articles-edit"]')
      ?.click();

    expect(router.navigate).toHaveBeenCalledWith(['/admin-panel/articles', 'typed-articles']);
    expect(service.getArticle).not.toHaveBeenCalled();
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
        id: '00000000000000000000000000000001',
        title: 'Typed articles',
        slug: 'typed-articles',
        folder: 'Engineering',
        folderId: 'folder-1',
        folderKey: 'engineering',
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
      ru: { title: 'Typed articles', content: '# Content' },
      en: { title: 'Typed articles', content: '# Content' },
    },
  };
}

function articlePayload(): AdminArticlePayload {
  return {
    slug: 'typed-articles',
    folderId: 'folder-1',
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
      ru: { title: 'Typed articles', content: '# Content' },
      en: { title: 'Typed articles', content: '# Content' },
    },
  };
}
