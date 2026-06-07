import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { ApiError } from '../models/api-error.model';
import { AuthModalService } from '../auth/auth-modal.service';
import { AuthSessionService } from '../auth/auth-session.service';
import { AuthTokenService } from '../auth/auth-token.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const tokenService = inject(AuthTokenService);
  const authModal = inject(AuthModalService);
  const authSession = inject(AuthSessionService);

  return next(req).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse) {
        if (error.status === 401) {
          tokenService.clearToken();
          authSession.clear();
          authModal.openLogin();
        }

        const body = error.error as Partial<ApiError> | null;
        const apiError: ApiError = {
          code: body?.code ?? 'unknown',
          type: body?.type ?? 'unknown',
          message: body?.message ?? error.message,
          status: error.status,
          location: body?.location ?? null,
          attr: body?.attr ?? null,
          nested_errors: body?.nested_errors,
        };
        return throwError(() => apiError);
      }
      return throwError(() => error);
    }),
  );
};
