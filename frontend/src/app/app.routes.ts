import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'about-me', pathMatch: 'full' },
  {
    path: 'ru',
    children: publicRoutes(),
  },
  {
    path: 'en',
    children: publicRoutes(),
  },
  ...publicRoutes(),
  {
    path: '404',
    loadChildren: () =>
      import('./features/not-found/not-found.routes').then((m) => m.notFoundRoutes),
  },
  {
    path: 'login',
    loadChildren: () => import('./features/auth/auth.routes').then((m) => m.authRoutes),
  },
  {
    path: 'admin-panel',
    canActivate: [authGuard],
    loadChildren: () =>
      import('./features/admin-panel/admin-panel.routes').then((m) => m.adminPanelRoutes),
  },
  { path: '**', redirectTo: '404' },
];

function publicRoutes(): Routes {
  return [
    {
      path: 'about-me',
      loadChildren: () => import('./features/about/about.routes').then((m) => m.aboutRoutes),
    },
    {
      path: 'competency-matrix',
      loadChildren: () => import('./features/matrix/matrix.routes').then((m) => m.matrixRoutes),
    },
    {
      path: 'notes',
      loadChildren: () => import('./features/notes/notes.routes').then((m) => m.notesRoutes),
    },
    {
      path: 'sitemap',
      loadChildren: () => import('./features/sitemap/sitemap.routes').then((m) => m.sitemapRoutes),
    },
  ];
}
