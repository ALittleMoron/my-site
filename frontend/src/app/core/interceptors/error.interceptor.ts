import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { ApiError } from '../models/api-error.model';

export const errorInterceptor: HttpInterceptorFn = (req, next) =>
  next(req).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse) {
        const body = error.error as Partial<ApiError> | null;
        const apiError: ApiError = {
          code: body?.code ?? 'unknown',
          type: body?.type ?? 'unknown',
          message: body?.message ?? error.message,
          location: body?.location ?? null,
          attr: body?.attr ?? null,
          nested_errors: body?.nested_errors,
        };
        return throwError(() => apiError);
      }
      return throwError(() => error);
    }),
  );
