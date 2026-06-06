import { authGuard } from './core/auth/auth.guard';
import { routes } from './app.routes';

describe('routes', () => {
  it('registers admin-panel as a protected top-level CSR route', () => {
    const adminRoute = routes.find((route) => route.path === 'admin-panel');

    expect(adminRoute).toBeDefined();
    expect(adminRoute?.canActivate).toEqual([authGuard]);
    expect(adminRoute?.loadChildren).toBeDefined();
  });
});
