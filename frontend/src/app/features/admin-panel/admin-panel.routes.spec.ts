import { teamGuard } from '../../core/auth/auth.guard';
import { adminPanelRoutes } from './admin-panel.routes';

describe('adminPanelRoutes', () => {
  it('keeps team-managed workspace routes behind the team guard', () => {
    const children = adminPanelRoutes[0].children ?? [];
    const teamWorkspaceRoutes = children.filter((route) =>
      route.path?.startsWith('workspace/team'),
    );
    const resumeWorkspaceRoutes = children.filter((route) =>
      route.path?.startsWith('workspace/resumes'),
    );
    const guardedPaths = new Set(
      [...teamWorkspaceRoutes, ...resumeWorkspaceRoutes].map((route) => route.path),
    );

    expect(guardedPaths).toEqual(
      new Set([
        'workspace/team',
        'workspace/team/:username',
        'workspace/resumes',
        'workspace/resumes/:id',
      ]),
    );
    for (const route of [...teamWorkspaceRoutes, ...resumeWorkspaceRoutes]) {
      expect(route.canActivate).toEqual([teamGuard]);
    }
  });
});
