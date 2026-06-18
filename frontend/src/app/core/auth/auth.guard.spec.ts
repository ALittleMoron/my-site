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
import { firstValueFrom, isObservable, of } from 'rxjs';
import { authGuard } from './auth.guard';
import { AuthService } from './auth.service';
import { ApiClient } from '../http/api-client.service';

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

  it('returns UrlTree redirect to /about-me when user cannot manage content', async () => {
    const result = await resolveGuardResult(runGuard(false));
    expect(result instanceof UrlTree).toBe(true);
    expect((result as UrlTree).toString()).toBe('/about-me');
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
