import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { ArticleAuthoringPreviewComponent } from './article-authoring-preview.component';

describe('ArticleAuthoringPreviewComponent', () => {
  let fixture: ComponentFixture<ArticleAuthoringPreviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ArticleAuthoringPreviewComponent],
      providers: [provideI18nTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(ArticleAuthoringPreviewComponent);
    fixture.componentRef.setInput('title', 'Typed articles');
    fixture.componentRef.setInput('content', 'Read [[articles:typed-article|typed article]].');
    fixture.componentRef.setInput('tags', [
      {
        id: '00000000000000000000000000000001',
        name: 'Angular',
        slug: 'angular',
        deletedAt: null,
        translations: { ru: { name: 'Angular' }, en: { name: 'Angular' } },
      },
    ]);
    fixture.componentRef.setInput('coverImageUrl', 'https://example.com/cover.jpg');
    fixture.componentRef.setInput('coverImageAlt', 'Cover alt');
    fixture.componentRef.setInput('seoTitle', 'SEO Typed articles');
    fixture.componentRef.setInput(
      'seoDescription',
      'SEO description for social cards and search snippets.',
    );
    fixture.componentRef.setInput('language', 'ru');
    fixture.detectChanges();
  });

  it('renders article content, tags, cover, and wiki links', () => {
    const text = fixture.nativeElement.textContent as string;
    const link = fixture.debugElement.query(By.css('.articles-preview-article a'))
      .nativeElement as HTMLAnchorElement;
    const cover = fixture.debugElement.query(By.css('.articles-preview-cover'))
      .nativeElement as HTMLImageElement;

    expect(text).toContain('Typed articles');
    expect(text).toContain('Angular');
    expect(link.getAttribute('href')).toBe('/ru/articles/typed-article');
    expect(cover.getAttribute('src')).toBe('https://example.com/cover.jpg');
    expect(cover.getAttribute('alt')).toBe('Cover alt');
  });

  it('renders social preview from SEO metadata', () => {
    const social = fixture.debugElement.query(By.css('.articles-social-preview'))
      .nativeElement as HTMLElement;

    expect(social.textContent).toContain('SEO Typed articles');
    expect(social.textContent).toContain('SEO description for social cards');
  });
});
