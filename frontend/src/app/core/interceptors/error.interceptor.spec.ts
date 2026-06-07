import { TestBed } from '@angular/core/testing';
import { HttpErrorResponse, HttpHandlerFn, HttpRequest } from '@angular/common/http';
import { throwError } from 'rxjs';
import { errorInterceptor } from './error.interceptor';
import { AuthTokenService } from '../auth/auth-token.service';
import { AuthModalService } from '../auth/auth-modal.service';
import { AuthSessionService } from '../auth/auth-session.service';

describe('errorInterceptor', () => {
  it('maps HttpErrorResponse to ApiError', (done) => {
    const req = new HttpRequest('GET', '/api/test');
    const next: HttpHandlerFn = () =>
      throwError(
        () =>
          new HttpErrorResponse({
            status: 500,
            error: { code: 'server_error', type: 'server_error', message: 'Broken' },
          }),
      );

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthTokenService, useValue: { clearToken: jest.fn() } },
        { provide: AuthModalService, useValue: { openLogin: jest.fn() } },
        { provide: AuthSessionService, useValue: { clear: jest.fn() } },
      ],
    });

    TestBed.runInInjectionContext(() => errorInterceptor(req, next)).subscribe({
      error: (err: unknown) => {
        expect(err).toEqual({
          code: 'server_error',
          type: 'server_error',
          message: 'Broken',
          status: 500,
          location: null,
          attr: null,
          nested_errors: undefined,
        });
        done();
      },
    });
  });

  it('opens login flow and clears local session on 401 responses', (done) => {
    const clearToken = jest.fn();
    const clearSession = jest.fn();
    const openLogin = jest.fn();
    const req = new HttpRequest('GET', '/api/protected');
    const next: HttpHandlerFn = () =>
      throwError(
        () =>
          new HttpErrorResponse({
            status: 401,
            error: { code: 'unauthorized', type: 'auth', message: 'Unauthorized' },
          }),
      );

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthTokenService, useValue: { clearToken } },
        { provide: AuthModalService, useValue: { openLogin } },
        { provide: AuthSessionService, useValue: { clear: clearSession } },
      ],
    });

    TestBed.runInInjectionContext(() => errorInterceptor(req, next)).subscribe({
      error: () => {
        expect(clearToken).toHaveBeenCalled();
        expect(clearSession).toHaveBeenCalled();
        expect(openLogin).toHaveBeenCalled();
        done();
      },
    });
  });

  it('preserves status when backend returns non-json error body', (done) => {
    const req = new HttpRequest('POST', '/api/competency-matrix/question-suggestions');
    const next: HttpHandlerFn = () =>
      throwError(
        () =>
          new HttpErrorResponse({
            status: 429,
            statusText: 'Too Many Requests',
            error: '<html>Too many requests</html>',
          }),
      );

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthTokenService, useValue: { clearToken: jest.fn() } },
        { provide: AuthModalService, useValue: { openLogin: jest.fn() } },
        { provide: AuthSessionService, useValue: { clear: jest.fn() } },
      ],
    });

    TestBed.runInInjectionContext(() => errorInterceptor(req, next)).subscribe({
      error: (err: unknown) => {
        expect(err).toEqual({
          code: 'unknown',
          type: 'unknown',
          message: expect.any(String),
          status: 429,
          location: null,
          attr: null,
          nested_errors: undefined,
        });
        done();
      },
    });
  });
});
