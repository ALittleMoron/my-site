import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'about-me', pathMatch: 'full' },
  {
    path: 'about-me',
    loadChildren: () => import('./features/about/about.routes').then(m => m.aboutRoutes),
  },
  {
    path: 'competency-matrix',
    loadChildren: () => import('./features/matrix/matrix.routes').then(m => m.matrixRoutes),
  },
  {
    path: 'sitemap',
    loadChildren: () => import('./features/sitemap/sitemap.routes').then(m => m.sitemapRoutes),
  },
  {
    path: '404',
    loadChildren: () => import('./features/not-found/not-found.routes').then(m => m.notFoundRoutes),
  },
  {
    path: 'login',
    loadChildren: () => import('./features/auth/auth.routes').then(m => m.authRoutes),
  },
  { path: '**', redirectTo: '404' },
];
