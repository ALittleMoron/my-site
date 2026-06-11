import { HttpRequest } from '@angular/common/http';
import { shouldTransferCacheRequest } from './app.config';

describe('appConfig HTTP transfer cache filter', () => {
  it('allows safe public GET requests used by SSR pages', () => {
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/i18n/languages'))).toBe(true);
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/i18n/bundles/ru'))).toBe(true);
    expect(
      shouldTransferCacheRequest(
        new HttpRequest('GET', 'http://localhost:8000/api/notes/detail/typed-notes?language=ru'),
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
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/notes/tags'))).toBe(true);
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/notes/tree'))).toBe(true);
  });

  it('excludes auth, private, analytics, and reaction requests', () => {
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/auth/me'))).toBe(false);
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/admin/notes/stats'))).toBe(
      false,
    );
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/admin/notes'))).toBe(false);
    expect(
      shouldTransferCacheRequest(
        new HttpRequest('POST', '/api/notes/detail/typed-notes/analytics/view', {}),
      ),
    ).toBe(false);
    expect(
      shouldTransferCacheRequest(
        new HttpRequest('POST', '/api/notes/detail/typed-notes/reaction', {}),
      ),
    ).toBe(false);
  });
});
