import { TestBed } from '@angular/core/testing';
import { Meta, Title } from '@angular/platform-browser';
import { provideI18nTesting } from '../../testing/i18n-testing';
import { SeoService } from './seo.service';

describe('SeoService', () => {
  let service: SeoService;
  let titleService: Title;
  let metaService: Meta;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideI18nTesting()],
    });
    service = TestBed.inject(SeoService);
    titleService = TestBed.inject(Title);
    metaService = TestBed.inject(Meta);
  });

  it('setMeta() sets document title using Title service', () => {
    service.setMeta({ title: 'Обо мне', description: 'Описание страницы.' });

    expect(titleService.getTitle()).toBe('Обо мне - Мой сайт');
  });

  it('setMeta() sets og:title meta tag', () => {
    service.setMeta({ title: 'Матрица компетенций', description: 'Матрица компетенций.' });

    const tag = metaService.getTag('property="og:title"');
    expect(tag?.content).toBe('Матрица компетенций - Мой сайт');
  });

  it('setMeta() sets description meta tag', () => {
    const description = 'Личный сайт Дмитрия Лунева.';
    service.setMeta({ title: 'Обо мне', description });

    const tag = metaService.getTag('name="description"');
    expect(tag?.content).toBe(description);
  });

  it('setMeta() creates canonical link from canonical path', () => {
    service.setMeta({
      title: 'Обо мне',
      description: 'Описание страницы.',
      canonicalPath: '/ru/about-me',
    });

    const link = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    expect(link?.href).toBe('http://localhost:4200/ru/about-me');
  });

  it('setMeta() removes stale canonical link when canonical is not provided', () => {
    service.setMeta({
      title: 'Обо мне',
      description: 'Описание страницы.',
      canonicalPath: '/about-me',
    });

    service.setMeta({ title: '404', description: 'Страница не найдена.' });

    expect(document.head.querySelector('link[rel="canonical"]')).toBeNull();
  });

  it('setMeta() writes language alternates', () => {
    service.setMeta({
      title: 'Typed notes',
      description: 'Description.',
      canonicalPath: '/ru/notes/typed-notes',
      alternates: [
        { language: 'ru', path: '/ru/notes/typed-notes' },
        { language: 'en', path: '/en/notes/typed-notes' },
      ],
    });

    const links = Array.from(
      document.head.querySelectorAll<HTMLLinkElement>('link[rel="alternate"][hreflang]'),
    );

    expect(links.map((link) => [link.hreflang, link.href])).toEqual([
      ['ru', 'http://localhost:4200/ru/notes/typed-notes'],
      ['en', 'http://localhost:4200/en/notes/typed-notes'],
    ]);
  });

  it('setMeta() writes JSON-LD structured data and removes stale data', () => {
    service.setMeta({
      title: 'Typed notes',
      description: 'Description.',
      structuredData: {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        headline: 'Typed notes',
      },
    });

    const script = document.head.querySelector<HTMLScriptElement>(
      'script[type="application/ld+json"]',
    );
    expect(script?.textContent).toContain('"@type":"BlogPosting"');

    service.setMeta({ title: '404', description: 'Not found.' });

    expect(document.head.querySelector('script[type="application/ld+json"]')).toBeNull();
  });

  it('setMeta() can mark a page as noindex', () => {
    service.setMeta({ title: '404', description: 'Not found.', robots: 'noindex, follow' });

    expect(metaService.getTag('name="robots"')?.content).toBe('noindex, follow');
  });
});
