import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import {
  ActivatedRouteSnapshot,
  GuardResult,
  MaybeAsync,
  RouterStateSnapshot,
  UrlTree,
} from '@angular/router';
import { provideRouter } from '@angular/router';
import { firstValueFrom, isObservable, of, throwError } from 'rxjs';
import { authGuard, teamGuard } from './auth.guard';
import { AuthService } from './auth.service';
import { ApiClient } from '../http/api-client.service';
import { I18nService } from '../i18n/i18n.service';

describe('authGuard', () => {
  function mockAuthService(canManageContent: boolean): Partial<AuthService> {
    return {
      canManageContent: () => canManageContent,
      ensureCurrentUserLoaded: () => of(void 0),
      clearLocalSession: jest.fn(),
    };
  }

  function runGuard(canManageContent: boolean): MaybeAsync<GuardResult> {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: mockAuthService(canManageContent) },
        { provide: I18nService, useValue: { language: signal('ru') } },
      ],
    });
    return TestBed.runInInjectionContext(() =>
      authGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    );
  }

  async function resolveGuardResult(result: MaybeAsync<GuardResult>): Promise<GuardResult> {
    if (isObservable(result)) {
      return firstValueFrom(result);
    }
    return Promise.resolve(result);
  }

  afterEach(() => {
    localStorage.clear();
  });

  it('returns true when user can manage content', async () => {
    await expect(resolveGuardResult(runGuard(true))).resolves.toBe(true);
  });

  it('returns UrlTree redirect to the localized public home when user cannot manage content', async () => {
    const result = await resolveGuardResult(runGuard(false));
    expect(result instanceof UrlTree).toBe(true);
    expect((result as UrlTree).toString()).toBe('/ru/how-this-site-is-built');
  });

  it('clears local session and redirects to localized public home when account restore fails', async () => {
    const clearLocalSession = jest.fn();
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: {
            ensureCurrentUserLoaded: () => throwError(() => new Error('restore failed')),
            clearLocalSession,
          },
        },
        { provide: I18nService, useValue: { language: signal('ru') } },
      ],
    });

    const result = await resolveGuardResult(
      TestBed.runInInjectionContext(() =>
        authGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
      ),
    );

    expect(clearLocalSession).toHaveBeenCalledTimes(1);
    expect(result instanceof UrlTree).toBe(true);
    expect((result as UrlTree).toString()).toBe('/ru/how-this-site-is-built');
  });

  it('waits for stored-token account restore before allowing admin-panel reload', async () => {
    localStorage.setItem('accessToken', 'existing-token');
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
        ApiClient,
        AuthService,
        { provide: I18nService, useValue: { language: signal('ru') } },
      ],
    });
    const httpMock = TestBed.inject(HttpTestingController);

    const result = TestBed.runInInjectionContext(() =>
      resolveGuardResult(authGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot)),
    );
    const accountReq = httpMock.expectOne((req) => req.url.includes('/api/account/base'));
    expect(accountReq.request.method).toBe('GET');
    accountReq.flush({ username: 'moderator', role: 'moderator' });

    await expect(result).resolves.toBe(true);
    httpMock.verify();
  });
});

describe('teamGuard', () => {
  function mockAuthService(canManageTeam: boolean): Partial<AuthService> {
    return {
      canManageTeam: () => canManageTeam,
      ensureCurrentUserLoaded: () => of(void 0),
      clearLocalSession: jest.fn(),
    };
  }

  function runGuard(canManageTeam: boolean): MaybeAsync<GuardResult> {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: mockAuthService(canManageTeam) },
        { provide: I18nService, useValue: { language: signal('ru') } },
      ],
    });
    return TestBed.runInInjectionContext(() =>
      teamGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    );
  }

  async function resolveGuardResult(result: MaybeAsync<GuardResult>): Promise<GuardResult> {
    if (isObservable(result)) {
      return firstValueFrom(result);
    }
    return Promise.resolve(result);
  }

  it('returns true when user can manage team', async () => {
    await expect(resolveGuardResult(runGuard(true))).resolves.toBe(true);
  });

  it('redirects non-team content managers away from team workspaces', async () => {
    const result = await resolveGuardResult(runGuard(false));

    expect(result instanceof UrlTree).toBe(true);
    expect((result as UrlTree).toString()).toBe('/admin-panel/articles');
  });

  it('clears local session and redirects to localized public home when team account restore fails', async () => {
    const clearLocalSession = jest.fn();
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: {
            ensureCurrentUserLoaded: () => throwError(() => new Error('restore failed')),
            clearLocalSession,
          },
        },
        { provide: I18nService, useValue: { language: signal('ru') } },
      ],
    });

    const result = await resolveGuardResult(
      TestBed.runInInjectionContext(() =>
        teamGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
      ),
    );

    expect(clearLocalSession).toHaveBeenCalledTimes(1);
    expect(result instanceof UrlTree).toBe(true);
    expect((result as UrlTree).toString()).toBe('/ru/how-this-site-is-built');
  });
});
