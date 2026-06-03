import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  {
    path: 'ru/notes/:slug',
    renderMode: RenderMode.Server,
  },
  {
    path: 'en/notes/:slug',
    renderMode: RenderMode.Server,
  },
  {
    path: 'ru/competency-matrix/questions/:slug',
    renderMode: RenderMode.Server,
  },
  {
    path: 'en/competency-matrix/questions/:slug',
    renderMode: RenderMode.Server,
  },
  {
    path: '**',
    renderMode: RenderMode.Client,
  },
];
