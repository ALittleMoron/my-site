import { Routes } from '@angular/router';

export const notesRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/notes-page/notes-page.component').then((m) => m.NotesPageComponent),
  },
  {
    path: ':slug',
    loadComponent: () =>
      import('./pages/notes-page/notes-page.component').then((m) => m.NotesPageComponent),
  },
];
