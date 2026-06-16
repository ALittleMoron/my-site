import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { ArticleDetailComponent } from './article-detail.component';

describe('ArticleDetailComponent', () => {
  let fixture: ComponentFixture<ArticleDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ArticleDetailComponent],
      providers: [provideI18nTesting()],
    }).compileComponents();
    fixture = TestBed.createComponent(ArticleDetailComponent);
    fixture.componentRef.setInput('article', {
      id: '00000000-0000-0000-0000-000000000001',
      title: 'Typed articles',
      slug: 'typed-articles',
      folder: 'Engineering',
      authorUsername: 'admin',
      publishedAt: '2026-01-02T03:04:05+00:00',
      publishStatus: 'Published',
      createdAt: '2026-01-01T03:04:05+00:00',
      updatedAt: '2026-01-03T03:04:05+00:00',
      excerpt: 'Excerpt',
      content: '# Content\n\nRead [[matrix:how-to-write-function|matrix question]].',
      metadata: {
        seoTitleRu: 'SEO Typed articles RU',
        seoTitleEn: 'SEO Typed articles EN',
        seoDescriptionRu:
          'SEO description RU with enough text to be useful for search snippets and social cards.',
        seoDescriptionEn:
          'SEO description EN with enough text to be useful for search snippets and social cards.',
        coverImageUrl: 'https://example.com/cover.jpg',
        coverImageAltRu: 'Cover image RU',
        coverImageAltEn: 'Cover image EN',
      },
      viewCount: 42,
      reactionCounts: { heart: 1, fire: 2, thinking: 3, neutral: 4, poop: 5 },
      tags: [
        {
          id: 1,
          name: 'Python',
          slug: 'python',
          deletedAt: null,
          translations: { ru: { name: 'Python' }, en: { name: 'Python' } },
        },
      ],
      translations: {
        ru: {
          title: 'Typed articles',
          content: '# Content\n\nRead [[matrix:how-to-write-function|matrix question]].',
          folder: 'Engineering',
        },
        en: {
          title: 'Typed articles',
          content: '# Content\n\nRead [[matrix:how-to-write-function|matrix question]].',
          folder: 'Engineering',
        },
      },
    });
    fixture.componentRef.setInput('selectedReaction', 'poop');
    fixture.componentRef.setInput('dateLocale', 'ru-RU');
    fixture.componentRef.setInput('language', 'en');
    fixture.detectChanges();
  });

  it('renders public view count and reaction counts', () => {
    const text = fixture.nativeElement.textContent as string;

    expect(text).toContain('42 просмотров');
    expect(text).toContain('5');
  });

  it('shows SEO analysis for admins on published and draft articles', () => {
    fixture.componentRef.setInput('canManageContent', true);
    fixture.detectChanges();

    let text = fixture.nativeElement.textContent as string;
    expect(text).toContain('SEO-анализ');
    expect(text).toContain('/articles/typed-articles');

    fixture.componentRef.setInput('article', {
      ...fixture.componentInstance.article()!,
      publishStatus: 'Draft',
      publishedAt: null,
    });
    fixture.detectChanges();

    text = fixture.nativeElement.textContent as string;
    expect(text).toContain('SEO-анализ');
  });

  it('hides SEO analysis from users without content access readers', () => {
    const text = fixture.nativeElement.textContent as string;

    expect(text).not.toContain('SEO-анализ');
  });

  it('emits selected reaction', () => {
    const reactionSelected = jest.fn();
    fixture.componentInstance.reactionSelected.subscribe(reactionSelected);

    const heartButton = fixture.debugElement.query(By.css('[aria-label="Понравилось"]'));
    heartButton.nativeElement.click();

    expect(reactionSelected).toHaveBeenCalledWith('heart');
  });

  it('renders typed wiki links to matrix questions', () => {
    const link = fixture.debugElement.query(By.css('.articles-markdown a'))
      .nativeElement as HTMLAnchorElement;

    expect(link.getAttribute('href')).toBe('/en/competency-matrix/questions/how-to-write-function');
    expect(link.textContent).toBe('matrix question');
  });

  it('renders admin action buttons with green edit and outline-only destructive/publish actions', () => {
    fixture.componentRef.setInput('canManageContent', true);
    fixture.componentRef.setInput('article', {
      ...fixture.componentInstance.article()!,
      publishStatus: 'Draft',
      publishedAt: null,
    });
    fixture.detectChanges();

    const buttons = Array.from(
      fixture.nativeElement.querySelectorAll('button'),
    ) as HTMLButtonElement[];
    const editButton = buttons.find((button) => button.textContent?.trim() === 'Редактировать');
    const publishButton = buttons.find((button) => button.textContent?.trim() === 'Опубликовать');
    const deleteButton = buttons.find((button) => button.textContent?.trim() === 'Удалить');

    expect(editButton?.classList).toContain('btn-success');
    expect(publishButton?.classList).toContain('btn-outline-success');
    expect(publishButton?.classList).not.toContain('btn-success');
    expect(deleteButton?.classList).toContain('btn-outline-danger');
    expect(deleteButton?.classList).not.toContain('btn-danger');
  });

  it('renders unpublish as an outline-only warning action', () => {
    fixture.componentRef.setInput('canManageContent', true);
    fixture.detectChanges();

    const unpublishButton = (
      Array.from(fixture.nativeElement.querySelectorAll('button')) as HTMLButtonElement[]
    ).find((button) => button.textContent?.includes('Снять с публикации'));

    expect(unpublishButton?.classList).toContain('btn-outline-warning');
    expect(unpublishButton?.classList).not.toContain('btn-warning');
  });
});
