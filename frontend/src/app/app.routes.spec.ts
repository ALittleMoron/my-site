import { authGuard } from './core/auth/auth.guard';
import { routes } from './app.routes';

describe('routes', () => {
  it('registers localized and legacy public routes for the site-build case study', () => {
    const russianRoutes = routes.find((route) => route.path === 'ru')?.children ?? [];
    const englishRoutes = routes.find((route) => route.path === 'en')?.children ?? [];
    const legacyRoutes = routes.filter((route) => route.path === 'how-this-site-is-built');

    expect(russianRoutes.find((route) => route.path === 'how-this-site-is-built')).toBeDefined();
    expect(englishRoutes.find((route) => route.path === 'how-this-site-is-built')).toBeDefined();
    expect(legacyRoutes).toHaveLength(1);
    expect(legacyRoutes[0]?.loadChildren).toBeDefined();
  });

  it('registers admin-panel as a protected top-level CSR route', () => {
    const adminRoute = routes.find((route) => route.path === 'admin-panel');

    expect(adminRoute).toBeDefined();
    expect(adminRoute?.canActivate).toEqual([authGuard]);
    expect(adminRoute?.loadChildren).toBeDefined();
  });
});
