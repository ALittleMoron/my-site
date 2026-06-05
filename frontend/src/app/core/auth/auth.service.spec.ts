import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { AuthService, AccountInfo } from './auth.service';
import { AuthTokenService } from './auth-token.service';
import { ApiClient } from '../http/api-client.service';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let tokenService: AuthTokenService;

  function setup(hasToken = false): void {
    localStorage.clear();
    if (hasToken) {
      localStorage.setItem('accessToken', 'existing-token');
    }

    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), ApiClient, AuthService],
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    tokenService = TestBed.inject(AuthTokenService);
  }

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  describe('login', () => {
    beforeEach(() => setup());

    it('stores token and loads user', () => {
      const mockAccount: AccountInfo = { username: 'moderator', role: 'moderator' };

      service.login('admin', 'secret').subscribe();

      const loginReq = httpMock.expectOne((req) => req.url.includes('/api/auth/login'));
      expect(loginReq.request.method).toBe('POST');
      loginReq.flush({ accessToken: 'new-token' });

      const accountReq = httpMock.expectOne((req) => req.url.includes('/api/account/base'));
      expect(accountReq.request.method).toBe('GET');
      accountReq.flush(mockAccount);

      expect(tokenService.token()).toBe('new-token');
      expect(service.currentUser()).toEqual(mockAccount);
      expect(service.isLoggedIn()).toBe(true);
      expect(service.canManageContent()).toBe(true);
    });
  });

  describe('logout', () => {
    beforeEach(() => setup());

    it('clears token and user', () => {
      service.currentUser.set({ username: 'admin', role: 'admin' });
      tokenService.setToken('some-token');

      service.logout().subscribe();

      const logoutReq = httpMock.expectOne((req) => req.url.includes('/api/auth/logout'));
      expect(logoutReq.request.method).toBe('POST');
      logoutReq.flush(null);

      expect(tokenService.token()).toBeNull();
      expect(service.currentUser()).toBeNull();
      expect(service.isLoggedIn()).toBe(false);
    });

    it('clears token and user when logout request fails', (done) => {
      service.currentUser.set({ username: 'admin', role: 'admin' });
      tokenService.setToken('some-token');

      service.logout().subscribe({
        next: () => {
          done.fail('Expected logout request to fail');
        },
        error: () => {
          expect(tokenService.token()).toBeNull();
          expect(service.currentUser()).toBeNull();
          expect(service.isLoggedIn()).toBe(false);
          done();
        },
      });

      const logoutReq = httpMock.expectOne((req) => req.url.includes('/api/auth/logout'));
      expect(logoutReq.request.method).toBe('POST');
      logoutReq.flush(
        { message: 'Logout failed' },
        { status: 500, statusText: 'Internal Server Error' },
      );
    });
  });

  describe('loadCurrentUser', () => {
    beforeEach(() => setup());

    it('populates currentUser signal', () => {
      const mockAccount: AccountInfo = { username: 'moderator', role: 'moderator' };

      service.loadCurrentUser().subscribe();

      const req = httpMock.expectOne((r) => r.url.includes('/api/account/base'));
      req.flush(mockAccount);

      expect(service.currentUser()).toEqual(mockAccount);
      expect(service.isLoggedIn()).toBe(true);
      expect(service.canManageContent()).toBe(true);
    });
  });

  describe('constructor with existing token', () => {
    it('calls loadCurrentUser when token exists', () => {
      setup(true);

      const req = httpMock.expectOne((r) => r.url.includes('/api/account/base'));
      req.flush({ username: 'admin', role: 'admin' });

      expect(service.currentUser()?.username).toBe('admin');
      expect(service.isAdmin()).toBe(true);
      expect(service.canManageContent()).toBe(true);
    });
  });
});
