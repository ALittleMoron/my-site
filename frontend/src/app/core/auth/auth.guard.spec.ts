import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { provideRouter } from '@angular/router';
import { authGuard } from './auth.guard';
import { AuthService } from './auth.service';

describe('authGuard', () => {
  function mockAuthService(canManageContent: boolean): Partial<AuthService> {
    return { canManageContent: () => canManageContent };
  }

  function runGuard(canManageContent: boolean): boolean | UrlTree {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: mockAuthService(canManageContent) },
      ],
    });
    return TestBed.runInInjectionContext(() =>
      authGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    ) as boolean | UrlTree;
  }

  it('returns true when user can manage content', () => {
    expect(runGuard(true)).toBe(true);
  });

  it('returns UrlTree redirect to /about-me when user cannot manage content', () => {
    const result = runGuard(false);
    expect(result instanceof UrlTree).toBe(true);
    expect((result as UrlTree).toString()).toBe('/about-me');
  });
});
