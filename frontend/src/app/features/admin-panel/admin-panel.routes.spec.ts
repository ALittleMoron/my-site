import { adminGuard } from '../../core/auth/auth.guard';
import { adminPanelRoutes } from './admin-panel.routes';

describe('adminPanelRoutes', () => {
  it('loads the shell page and workspace resume routes at the feature root', async () => {
    expect(adminPanelRoutes.map((route) => route.path)).toEqual(['']);
    expect(adminPanelRoutes[0].loadComponent).toBeDefined();
    expect(adminPanelRoutes[0].children?.map((route) => route.path)).toEqual([
      '',
      'articles',
      'matrix-questions',
      'matrix-question-queue',
      'workspace/resumes',
      'workspace/resumes/:id',
    ]);

    const resumeRoutes = adminPanelRoutes[0].children?.filter((route) =>
      route.path?.startsWith('workspace/resumes'),
    );
    expect(resumeRoutes?.length).toBe(2);
    expect(resumeRoutes?.[0].canActivate).toEqual([adminGuard]);
    expect(resumeRoutes?.[1].canActivate).toEqual([adminGuard]);
    await expect(resumeRoutes?.[0].loadComponent?.()).resolves.toBeDefined();
    await expect(resumeRoutes?.[1].loadComponent?.()).resolves.toBeDefined();
  });
});
