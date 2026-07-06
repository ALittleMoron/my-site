import { teamGuard } from '../../core/auth/auth.guard';
import { adminPanelRoutes } from './admin-panel.routes';

describe('adminPanelRoutes', () => {
  it('loads the shell page and team-managed workspace routes at the feature root', async () => {
    expect(adminPanelRoutes.map((route) => route.path)).toEqual(['']);
    expect(adminPanelRoutes[0].loadComponent).toBeDefined();
    expect(adminPanelRoutes[0].children?.map((route) => route.path)).toEqual([
      '',
      'articles',
      'article-folders',
      'article-statistics',
      'articles/:slug',
      'matrix-questions',
      'matrix-structure',
      'matrix-questions/:id',
      'matrix-question-queue',
      'workspace/team',
      'workspace/team/:username',
      'workspace/resumes',
      'workspace/resumes/:id',
    ]);

    const teamRoutes = adminPanelRoutes[0].children?.filter((route) =>
      route.path?.startsWith('workspace/team'),
    );
    const resumeRoutes = adminPanelRoutes[0].children?.filter((route) =>
      route.path?.startsWith('workspace/resumes'),
    );
    expect(teamRoutes?.length).toBe(2);
    expect(teamRoutes?.[0].canActivate).toEqual([teamGuard]);
    expect(teamRoutes?.[1].canActivate).toEqual([teamGuard]);
    expect(resumeRoutes?.length).toBe(2);
    expect(resumeRoutes?.[0].canActivate).toEqual([teamGuard]);
    expect(resumeRoutes?.[1].canActivate).toEqual([teamGuard]);
    await expect(
      adminPanelRoutes[0].children
        ?.find((route) => route.path === 'article-folders')
        ?.loadComponent?.(),
    ).resolves.toBeDefined();
    await expect(
      adminPanelRoutes[0].children
        ?.find((route) => route.path === 'article-statistics')
        ?.loadComponent?.(),
    ).resolves.toBeDefined();
    await expect(
      adminPanelRoutes[0].children
        ?.find((route) => route.path === 'articles/:slug')
        ?.loadComponent?.(),
    ).resolves.toBeDefined();
    await expect(
      adminPanelRoutes[0].children
        ?.find((route) => route.path === 'matrix-questions/:id')
        ?.loadComponent?.(),
    ).resolves.toBeDefined();
    await expect(teamRoutes?.[0].loadComponent?.()).resolves.toBeDefined();
    await expect(teamRoutes?.[1].loadComponent?.()).resolves.toBeDefined();
    await expect(resumeRoutes?.[0].loadComponent?.()).resolves.toBeDefined();
    await expect(resumeRoutes?.[1].loadComponent?.()).resolves.toBeDefined();
  });
});
