import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { provideRouter } from '@angular/router';
import { authGuard } from './auth.guard';
import { AuthService } from './auth.service';

describe('authGuard', () => {
  function mockAuthService(isAdmin: boolean): Partial<AuthService> {
    return { isAdmin: () => isAdmin };
  }

  function runGuard(isAdmin: boolean): boolean | UrlTree {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: mockAuthService(isAdmin) },
      ],
    });
    return TestBed.runInInjectionContext(() =>
      authGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    ) as boolean | UrlTree;
  }

  it('returns true when user is admin', () => {
    expect(runGuard(true)).toBe(true);
  });

  it('returns UrlTree redirect to /about-me when user is not admin', () => {
    const result = runGuard(false);
    expect(result instanceof UrlTree).toBe(true);
    expect((result as UrlTree).toString()).toBe('/about-me');
  });
});
