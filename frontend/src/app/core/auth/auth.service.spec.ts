import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { AuthService, AccountInfo } from './auth.service';
import { AuthTokenService } from './auth-token.service';
import { ApiClient } from '../http/api-client.service';
import { SKIP_AUTH_HEADER, SKIP_AUTH_REFRESH } from './auth-http-context';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let tokenService: AuthTokenService;

  function setup(): void {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), ApiClient, AuthService],
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    tokenService = TestBed.inject(AuthTokenService);
  }

  beforeEach(() => setup());

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  describe('login', () => {
    it('stores token and loads user', () => {
      const mockAccount: AccountInfo = { username: 'moderator', role: 'moderator' };

      service.login('admin', 'secret').subscribe();

      const loginReq = httpMock.expectOne((req) => req.url.includes('/api/auth/login'));
      expect(loginReq.request.method).toBe('POST');
      expect(loginReq.request.withCredentials).toBe(true);
      loginReq.flush({ accessToken: 'new-token', accessTokenExpiresInSeconds: 900 });

      const accountReq = httpMock.expectOne((req) => req.url.includes('/api/account/base'));
      expect(accountReq.request.method).toBe('GET');
      accountReq.flush(mockAccount);

      expect(tokenService.token()).toBe('new-token');
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(service.currentUser()).toEqual(mockAccount);
      expect(service.isLoggedIn()).toBe(true);
      expect(service.canManageContent()).toBe(true);
      expect(service.canManageTeam()).toBe(false);
    });
  });

  describe('refreshAccessToken', () => {
    it('refreshes the in-memory access token from the session cookie', () => {
      service.refreshAccessToken().subscribe();

      const refreshReq = httpMock.expectOne((req) => req.url.includes('/api/auth/refresh'));
      expect(refreshReq.request.method).toBe('POST');
      expect(refreshReq.request.withCredentials).toBe(true);
      expect(refreshReq.request.headers.get('X-CSRF-Guard')).toBe('1');
      expect(refreshReq.request.context.get(SKIP_AUTH_REFRESH)).toBe(true);
      expect(refreshReq.request.context.get(SKIP_AUTH_HEADER)).toBe(true);
      refreshReq.flush({ accessToken: 'fresh-token', accessTokenExpiresInSeconds: 900 });

      expect(tokenService.token()).toBe('fresh-token');
    });

    it('shares a concurrent refresh request', () => {
      let completions = 0;

      service.refreshAccessToken().subscribe(() => {
        completions += 1;
      });
      service.refreshAccessToken().subscribe(() => {
        completions += 1;
      });

      const refreshRequests = httpMock.match((req) => req.url.includes('/api/auth/refresh'));
      expect(refreshRequests).toHaveLength(1);
      refreshRequests[0].flush({ accessToken: 'shared-token', accessTokenExpiresInSeconds: 900 });

      expect(completions).toBe(2);
      expect(tokenService.token()).toBe('shared-token');
    });
  });

  describe('restoreSession', () => {
    it('restores auth state from refresh and current account on startup', () => {
      const mockAccount: AccountInfo = { username: 'owner', role: 'owner' };
      let completed = false;

      service.restoreSession().subscribe(() => {
        completed = true;
      });

      const refreshReq = httpMock.expectOne((req) => req.url.includes('/api/auth/refresh'));
      refreshReq.flush({ accessToken: 'startup-token', accessTokenExpiresInSeconds: 900 });

      const accountReq = httpMock.expectOne((req) => req.url.includes('/api/account/base'));
      accountReq.flush(mockAccount);

      expect(completed).toBe(true);
      expect(tokenService.token()).toBe('startup-token');
      expect(service.currentUser()).toEqual(mockAccount);
      expect(service.canManageContent()).toBe(true);
      expect(service.canManageTeam()).toBe(true);
    });

    it('clears local state and completes when startup refresh is rejected', () => {
      tokenService.setToken('stale-token');
      service.currentUser.set({ username: 'admin', role: 'admin' });
      let completed = false;

      service.restoreSession().subscribe(() => {
        completed = true;
      });

      const refreshReq = httpMock.expectOne((req) => req.url.includes('/api/auth/refresh'));
      refreshReq.flush({ message: 'Unauthorized' }, { status: 401, statusText: 'Unauthorized' });

      expect(completed).toBe(true);
      expect(tokenService.token()).toBeNull();
      expect(service.currentUser()).toBeNull();
      httpMock.expectNone((req) => req.url.includes('/api/account/base'));
    });
  });

  describe('logout', () => {
    it('clears token and user', () => {
      service.currentUser.set({ username: 'admin', role: 'admin' });
      tokenService.setToken('some-token');

      service.logout().subscribe();

      const logoutReq = httpMock.expectOne((req) => req.url.includes('/api/auth/logout'));
      expect(logoutReq.request.method).toBe('POST');
      expect(logoutReq.request.withCredentials).toBe(true);
      expect(logoutReq.request.headers.get('X-CSRF-Guard')).toBe('1');
      expect(logoutReq.request.context.get(SKIP_AUTH_REFRESH)).toBe(true);
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
      expect(logoutReq.request.headers.get('X-CSRF-Guard')).toBe('1');
      logoutReq.flush(
        { message: 'Logout failed' },
        { status: 500, statusText: 'Internal Server Error' },
      );
    });
  });

  describe('loadCurrentUser', () => {
    it('populates currentUser signal', () => {
      const mockAccount: AccountInfo = { username: 'moderator', role: 'moderator' };

      service.loadCurrentUser().subscribe();

      const req = httpMock.expectOne((r) => r.url.includes('/api/account/base'));
      req.flush(mockAccount);

      expect(service.currentUser()).toEqual(mockAccount);
      expect(service.isLoggedIn()).toBe(true);
      expect(service.canManageContent()).toBe(true);
      expect(service.canManageTeam()).toBe(false);
    });
  });

  describe('ensureCurrentUserLoaded', () => {
    it('does not request current account when there is no in-memory token', () => {
      let completed = false;

      service.ensureCurrentUserLoaded().subscribe(() => {
        completed = true;
      });

      httpMock.expectNone((r) => r.url.includes('/api/account/base'));
      expect(completed).toBe(true);
      expect(service.currentUser()).toBeNull();
    });

    it('restores current user when a token is already in memory', () => {
      const mockAccount: AccountInfo = { username: 'owner', role: 'owner' };
      tokenService.setToken('existing-token');
      let completed = false;

      service.ensureCurrentUserLoaded().subscribe(() => {
        completed = true;
      });
      const req = httpMock.expectOne((r) => r.url.includes('/api/account/base'));
      expect(req.request.method).toBe('GET');
      req.flush(mockAccount);

      expect(completed).toBe(true);
      expect(service.currentUser()).toEqual(mockAccount);
      expect(service.canManageContent()).toBe(true);
      expect(service.canManageTeam()).toBe(true);
    });

    it('shares the in-flight account restore request', () => {
      const mockAccount: AccountInfo = { username: 'admin', role: 'admin' };
      tokenService.setToken('existing-token');
      let completions = 0;

      service.ensureCurrentUserLoaded().subscribe(() => {
        completions += 1;
      });
      service.ensureCurrentUserLoaded().subscribe(() => {
        completions += 1;
      });
      const requests = httpMock.match((r) => r.url.includes('/api/account/base'));
      expect(requests).toHaveLength(1);
      requests[0].flush(mockAccount);

      expect(completions).toBe(2);
      expect(service.currentUser()).toEqual(mockAccount);
    });

    it('clears the local session when account restore fails', () => {
      tokenService.setToken('existing-token');
      let failed = false;

      service.ensureCurrentUserLoaded().subscribe({
        error: () => {
          failed = true;
        },
      });
      const req = httpMock.expectOne((r) => r.url.includes('/api/account/base'));
      req.flush({ message: 'Unauthorized' }, { status: 401, statusText: 'Unauthorized' });

      expect(failed).toBe(true);
      expect(tokenService.token()).toBeNull();
      expect(service.currentUser()).toBeNull();
    });
  });
});
