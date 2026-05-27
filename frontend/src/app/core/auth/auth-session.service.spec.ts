import { TestBed } from '@angular/core/testing';
import { AuthSessionService } from './auth-session.service';

describe('AuthSessionService', () => {
  let service: AuthSessionService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AuthSessionService);
  });

  it('tracks current user and derived auth state', () => {
    service.setCurrentUser({ username: 'admin', role: 'Admin' });

    expect(service.currentUser()).toEqual({ username: 'admin', role: 'Admin' });
    expect(service.isLoggedIn()).toBe(true);
    expect(service.isAdmin()).toBe(true);
  });

  it('clears current user', () => {
    service.setCurrentUser({ username: 'admin', role: 'Admin' });

    service.clear();

    expect(service.currentUser()).toBeNull();
    expect(service.isLoggedIn()).toBe(false);
    expect(service.isAdmin()).toBe(false);
  });
});
