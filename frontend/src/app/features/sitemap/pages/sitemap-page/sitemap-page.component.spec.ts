import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { SeoService } from '../../../../core/seo/seo.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { SitemapNotesService } from '../../services/sitemap-notes.service';
import { SitemapPageComponent } from './sitemap-page.component';

describe('SitemapPageComponent', () => {
  let fixture: ComponentFixture<SitemapPageComponent>;
  let sitemapNotesService: { getPublishedNotes: jest.Mock };
  let seoService: { setTranslatedMeta: jest.Mock };

  beforeEach(async () => {
    sitemapNotesService = {
      getPublishedNotes: jest.fn().mockReturnValue(
        of([
          {
            title: 'Typed notes',
            slug: 'typed-notes',
          },
        ]),
      ),
    };
    seoService = {
      setTranslatedMeta: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [SitemapPageComponent],
      providers: [
        provideRouter([]),
        provideI18nTesting(),
        { provide: SeoService, useValue: seoService },
        { provide: SitemapNotesService, useValue: sitemapNotesService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(SitemapPageComponent);
  });

  it('renders localized links to published notes', () => {
    fixture.detectChanges();

    const link = fixture.nativeElement.querySelector(
      '[data-testid="sitemap-note-link"]',
    ) as HTMLAnchorElement;

    expect(sitemapNotesService.getPublishedNotes).toHaveBeenCalledWith('ru');
    expect(fixture.nativeElement.textContent).toContain('Опубликованные заметки');
    expect(link.textContent?.trim()).toBe('Typed notes');
    expect(link.getAttribute('href')).toBe('/ru/notes/typed-notes');
  });

  it('renders a localized link to the site-build case study', () => {
    fixture.detectChanges();

    const link = fixture.nativeElement.querySelector(
      'a[href="/ru/how-this-site-is-built"]',
    ) as HTMLAnchorElement | null;

    expect(link).not.toBeNull();
    expect(fixture.nativeElement.textContent).toContain('Как устроен сайт');
  });
});
