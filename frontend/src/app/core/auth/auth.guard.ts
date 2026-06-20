import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.ensureCurrentUserLoaded().pipe(
    map(() => auth.canManageContent() || router.createUrlTree(['/about-me'])),
    catchError(() => {
      auth.clearLocalSession();
      return of(router.createUrlTree(['/about-me']));
    }),
  );
};

export const adminGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.ensureCurrentUserLoaded().pipe(
    map(() => auth.isAdmin() || router.createUrlTree(['/admin-panel/articles'])),
    catchError(() => {
      auth.clearLocalSession();
      return of(router.createUrlTree(['/about-me']));
    }),
  );
};
