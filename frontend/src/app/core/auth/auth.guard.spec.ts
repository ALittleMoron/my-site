import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { authGuard } from './auth.guard';

describe('authGuard', () => {
  const runGuard = (): boolean =>
    TestBed.runInInjectionContext(() =>
      authGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    ) as boolean;

  it('should return true (stub — always allows access)', () => {
    expect(runGuard()).toBe(true);
  });
});
