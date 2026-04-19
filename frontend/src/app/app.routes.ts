import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'matrix', pathMatch: 'full' },
  {
    path: 'matrix',
    loadChildren: () =>
      import('./features/matrix/matrix.routes').then(m => m.matrixRoutes),
  },
];
