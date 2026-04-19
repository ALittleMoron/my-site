import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'matrix', pathMatch: 'full' },
  {
    path: 'matrix',
    canActivate: [authGuard],
    loadChildren: () =>
      import('./features/matrix/matrix.routes').then(m => m.matrixRoutes),
  },
];
