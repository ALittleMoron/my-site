import { DOCUMENT } from '@angular/core';
import { TestBed } from '@angular/core/testing';

import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ApiClient } from '../http/api-client.service';
import { I18nService } from './i18n.service';

describe('I18nService', () => {
  let service: I18nService;
  let httpMock: HttpTestingController;
  let document: Document;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [ApiClient, I18nService, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(I18nService);
    httpMock = TestBed.inject(HttpTestingController);
    document = TestBed.inject(DOCUMENT);
  });

  afterEach(() => httpMock.verify());

  it('loads languages before the default bundle during startup', () => {
    service.initialize().subscribe();

    const languagesReq = httpMock.expectOne((req) => req.url.endsWith('/api/i18n/languages'));
    expect(languagesReq.request.method).toBe('GET');
    languagesReq.flush({
      defaultLanguage: 'ru',
      languages: [
        { code: 'ru', label: 'Русский' },
        { code: 'en', label: 'English' },
      ],
    });

    const bundleReq = httpMock.expectOne((req) => req.url.endsWith('/api/i18n/bundles/ru'));
    bundleReq.flush({
      language: 'ru',
      messages: {
        'shell.nav.about': 'Обо мне',
        greeting: 'Привет, {name}',
      },
    });

    expect(service.language()).toBe('ru');
    expect(service.languages()).toEqual([
      { code: 'ru', label: 'Русский' },
      { code: 'en', label: 'English' },
    ]);
    expect(service.translate('shell.nav.about')).toBe('Обо мне');
    expect(service.translate('greeting', { name: 'Дима' })).toBe('Привет, Дима');
    expect(document.documentElement.lang).toBe('ru');
  });

  it('uses the stored language when it is still available', () => {
    localStorage.setItem('chosenLanguage', 'en');

    service.initialize().subscribe();
    httpMock
      .expectOne((req) => req.url.endsWith('/api/i18n/languages'))
      .flush({
        defaultLanguage: 'ru',
        languages: [
          { code: 'ru', label: 'Русский' },
          { code: 'en', label: 'English' },
        ],
      });

    const bundleReq = httpMock.expectOne((req) => req.url.endsWith('/api/i18n/bundles/en'));
    bundleReq.flush({ language: 'en', messages: { 'shell.nav.about': 'About' } });

    expect(service.language()).toBe('en');
    expect(service.translate('shell.nav.about')).toBe('About');
  });

  it('uses the URL language prefix before the stored language', () => {
    window.history.pushState({}, '', '/en/articles/typed-articles');
    localStorage.setItem('chosenLanguage', 'ru');

    service.initialize().subscribe();
    httpMock
      .expectOne((req) => req.url.endsWith('/api/i18n/languages'))
      .flush({
        defaultLanguage: 'ru',
        languages: [
          { code: 'ru', label: 'Русский' },
          { code: 'en', label: 'English' },
        ],
      });

    const bundleReq = httpMock.expectOne((req) => req.url.endsWith('/api/i18n/bundles/en'));
    bundleReq.flush({ language: 'en', messages: { 'shell.nav.about': 'About' } });

    expect(service.language()).toBe('en');
    expect(localStorage.getItem('chosenLanguage')).toBe('en');
    window.history.pushState({}, '', '/');
  });

  it('ignores a stale stored language and uses backend default language', () => {
    localStorage.setItem('chosenLanguage', 'de');

    service.initialize().subscribe();
    httpMock
      .expectOne((req) => req.url.endsWith('/api/i18n/languages'))
      .flush({
        defaultLanguage: 'ru',
        languages: [
          { code: 'ru', label: 'Русский' },
          { code: 'en', label: 'English' },
        ],
      });

    const bundleReq = httpMock.expectOne((req) => req.url.endsWith('/api/i18n/bundles/ru'));
    bundleReq.flush({ language: 'ru', messages: { 'shell.nav.about': 'Обо мне' } });

    expect(service.language()).toBe('ru');
    expect(localStorage.getItem('chosenLanguage')).toBe('ru');
  });

  it('switches language and reuses a cached bundle', () => {
    service.initialize().subscribe();
    httpMock
      .expectOne((req) => req.url.endsWith('/api/i18n/languages'))
      .flush({
        defaultLanguage: 'ru',
        languages: [
          { code: 'ru', label: 'Русский' },
          { code: 'en', label: 'English' },
        ],
      });
    httpMock
      .expectOne((req) => req.url.endsWith('/api/i18n/bundles/ru'))
      .flush({ language: 'ru', messages: { title: 'Заголовок' } });

    service.switchLanguage('en').subscribe();
    httpMock
      .expectOne((req) => req.url.endsWith('/api/i18n/bundles/en'))
      .flush({ language: 'en', messages: { title: 'Title' } });
    expect(service.translate('title')).toBe('Title');
    expect(localStorage.getItem('chosenLanguage')).toBe('en');

    service.switchLanguage('ru').subscribe();
    httpMock.expectNone((req) => req.url.includes('/api/i18n/bundles/ru'));
    expect(service.translate('title')).toBe('Заголовок');
    expect(localStorage.getItem('chosenLanguage')).toBe('ru');
  });

  it('records startup error when languages cannot be loaded', () => {
    service.initialize().subscribe();

    httpMock
      .expectOne((req) => req.url.endsWith('/api/i18n/languages'))
      .flush({ detail: 'unavailable' }, { status: 500, statusText: 'Server Error' });

    expect(service.startupError()).toBe(true);
    expect(service.translate('i18n.startupError.title')).toBe('Failed to load localization');
  });
});
