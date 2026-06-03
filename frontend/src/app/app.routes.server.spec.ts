jest.mock('@angular/ssr', () => ({
  RenderMode: {
    Server: 0,
    Client: 1,
    Prerender: 2,
  },
}));

import { RenderMode } from '@angular/ssr';
import { serverRoutes } from './app.routes.server';

describe('serverRoutes', () => {
  it('server-renders only localized public detail pages', () => {
    expect(serverRoutes).toEqual(
      expect.arrayContaining([
        { path: 'ru/notes/:slug', renderMode: RenderMode.Server },
        { path: 'en/notes/:slug', renderMode: RenderMode.Server },
        { path: 'ru/competency-matrix/questions/:slug', renderMode: RenderMode.Server },
        { path: 'en/competency-matrix/questions/:slug', renderMode: RenderMode.Server },
      ]),
    );
    expect(serverRoutes.find((route) => route.path === 'ru/competency-matrix')).toBeUndefined();
    expect(serverRoutes.find((route) => route.path === 'en/competency-matrix')).toBeUndefined();
  });

  it('keeps the rest of the Angular app in CSR mode', () => {
    expect(serverRoutes.at(-1)).toEqual({ path: '**', renderMode: RenderMode.Client });
  });
});
