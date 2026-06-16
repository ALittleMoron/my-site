jest.mock('@angular/router', () => {
  const actual = jest.requireActual('@angular/router') as typeof import('@angular/router');

  return {
    ...actual,
    withInMemoryScrolling: jest.fn(actual.withInMemoryScrolling),
  };
});

import { HttpRequest } from '@angular/common/http';
import { withInMemoryScrolling } from '@angular/router';
import { shouldTransferCacheRequest } from './app.config';

describe('appConfig router scrolling', () => {
  it('starts regular route navigations at the top while preserving anchor scrolling', () => {
    expect(withInMemoryScrolling).toHaveBeenCalledWith({
      anchorScrolling: 'enabled',
      scrollPositionRestoration: 'enabled',
    });
  });
});

describe('appConfig HTTP transfer cache filter', () => {
  it('allows safe public GET requests used by SSR pages', () => {
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/i18n/languages'))).toBe(true);
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/i18n/bundles/ru'))).toBe(true);
    expect(
      shouldTransferCacheRequest(
        new HttpRequest(
          'GET',
          'http://localhost:8000/api/articles/detail/typed-articles?language=ru',
        ),
      ),
    ).toBe(true);
    expect(
      shouldTransferCacheRequest(
        new HttpRequest(
          'GET',
          'http://localhost:8000/api/competency-matrix/items/public/how-to-write-function?language=ru',
        ),
      ),
    ).toBe(true);
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/articles/tags'))).toBe(true);
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/articles/tree'))).toBe(true);
  });

  it('excludes auth, private, analytics, and reaction requests', () => {
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/auth/me'))).toBe(false);
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/admin/articles/stats'))).toBe(
      false,
    );
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/admin/articles'))).toBe(false);
    expect(
      shouldTransferCacheRequest(
        new HttpRequest('POST', '/api/articles/detail/typed-articles/analytics/view', {}),
      ),
    ).toBe(false);
    expect(
      shouldTransferCacheRequest(
        new HttpRequest('POST', '/api/articles/detail/typed-articles/reaction', {}),
      ),
    ).toBe(false);
  });
});
