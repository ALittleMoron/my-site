import { Routes } from '@angular/router';

export const adminPanelRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/admin-panel-page/admin-panel-page.component').then(
        (m) => m.AdminPanelPageComponent,
      ),
  },
];
