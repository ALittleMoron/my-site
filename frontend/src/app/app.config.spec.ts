import { HttpRequest } from '@angular/common/http';
import { shouldRestoreAuthOnStartup, shouldTransferCacheRequest } from './app.config';

describe('appConfig HTTP transfer cache filter', () => {
  it('allows safe public GET requests used by SSR pages', () => {
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
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/i18n/languages'))).toBe(false);
    expect(shouldTransferCacheRequest(new HttpRequest('GET', '/api/i18n/bundles/ru'))).toBe(false);
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

describe('appConfig auth startup', () => {
  it('skips auth restore probes on public routes', () => {
    expect(shouldRestoreAuthOnStartup('/ru/how-this-site-is-built')).toBe(false);
    expect(shouldRestoreAuthOnStartup('/en/articles/typed-articles')).toBe(false);
    expect(shouldRestoreAuthOnStartup('/ru/competency-matrix')).toBe(false);
    expect(
      shouldRestoreAuthOnStartup('/ru/competency-matrix/questions/how-to-write-function'),
    ).toBe(false);
  });

  it('restores auth on protected admin routes', () => {
    expect(shouldRestoreAuthOnStartup('/admin-panel')).toBe(true);
    expect(shouldRestoreAuthOnStartup('/admin-panel/articles')).toBe(true);
  });
});
