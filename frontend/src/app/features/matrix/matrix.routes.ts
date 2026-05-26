import { Routes } from '@angular/router';

export const matrixRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/matrix-list/matrix-list.component').then((m) => m.MatrixListComponent),
  },
];
