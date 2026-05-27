import { TestBed } from '@angular/core/testing';
import { Meta, Title } from '@angular/platform-browser';
import { SeoService } from './seo.service';

describe('SeoService', () => {
  let service: SeoService;
  let titleService: Title;
  let metaService: Meta;

  beforeEach(() => {
    TestBed.configureTestingModule({});
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
      canonicalPath: '/about-me',
    });

    const link = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    expect(link?.href).toBe('http://localhost:4200/about-me');
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
});
