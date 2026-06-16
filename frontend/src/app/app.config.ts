import {
  ApplicationConfig,
  ErrorHandler,
  inject,
  provideAppInitializer,
  provideZoneChangeDetection,
  InjectionToken,
} from '@angular/core';
import { HttpRequest, provideHttpClient, withInterceptors } from '@angular/common/http';
import {
  provideClientHydration,
  withEventReplay,
  withHttpTransferCacheOptions,
} from '@angular/platform-browser';
import { provideRouter, withComponentInputBinding, withInMemoryScrolling } from '@angular/router';
import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { errorInterceptor } from './core/interceptors/error.interceptor';
import { GlobalErrorHandler } from './core/error/global-error-handler';
import { I18nService } from './core/i18n/i18n.service';
import { of } from 'rxjs';

export const SKIP_I18N_STARTUP = new InjectionToken<boolean>('SKIP_I18N_STARTUP', {
  providedIn: 'root',
  factory: () => false,
});

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(
      routes,
      withComponentInputBinding(),
      withInMemoryScrolling({ anchorScrolling: 'enabled', scrollPositionRestoration: 'enabled' }),
    ),
    provideClientHydration(
      withEventReplay(),
      withHttpTransferCacheOptions({ filter: shouldTransferCacheRequest }),
    ),
    provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),
    provideAppInitializer(() => initializeI18n()),
    { provide: ErrorHandler, useClass: GlobalErrorHandler },
  ],
};

function initializeI18n() {
  if (inject(SKIP_I18N_STARTUP)) {
    return of(void 0);
  }
  return inject(I18nService).initialize();
}

export function shouldTransferCacheRequest(req: HttpRequest<unknown>): boolean {
  if (req.method !== 'GET') return false;

  const pathname = readPathname(req.url);
  return (
    pathname === '/api/i18n/languages' ||
    pathname.startsWith('/api/i18n/bundles/') ||
    pathname.startsWith('/api/articles/detail/') ||
    pathname.startsWith('/api/competency-matrix/items/public/') ||
    pathname === '/api/articles/tags' ||
    pathname === '/api/articles/tree' ||
    pathname === '/api/articles'
  );
}

function readPathname(url: string): string {
  return new URL(url, 'http://localhost').pathname;
}
