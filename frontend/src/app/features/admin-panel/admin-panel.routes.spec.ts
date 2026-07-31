import { ownerGuard, teamGuard } from '../../core/auth/auth.guard';
import { adminUnsavedChangesGuard } from './guards/admin-unsaved-changes.guard';
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

  it('registers the article tag workspace with unsaved-change protection', () => {
    const tagRoute = (adminPanelRoutes[0].children ?? []).find(
      (route) => route.path === 'article-tags',
    );

    expect(tagRoute).toBeDefined();
    expect(tagRoute?.canDeactivate).toEqual([adminUnsavedChangesGuard]);
  });

  it('keeps agent client management behind the owner guard', () => {
    const route = (adminPanelRoutes[0].children ?? []).find(
      (child) => child.path === 'workspace/agent-clients',
    );

    expect(route).toBeDefined();
    expect(route?.canActivate).toEqual([ownerGuard]);
    expect(route?.canDeactivate).toEqual([adminUnsavedChangesGuard]);
  });

  it('keeps operational tools behind the owner and admin team guard', () => {
    const route = (adminPanelRoutes[0].children ?? []).find(
      (child) => child.path === 'workspace/tools',
    );

    expect(route).toBeDefined();
    expect(route?.canActivate).toEqual([teamGuard]);
  });

  it('keeps both private People routes behind the team and unsaved-change guards', () => {
    const routes = (adminPanelRoutes[0].children ?? []).filter((child) =>
      child.path?.startsWith('knowledge/people'),
    );

    expect(routes.map((route) => route.path)).toEqual(['knowledge/people', 'knowledge/people/:id']);
    for (const route of routes) {
      expect(route.canActivate).toEqual([teamGuard]);
      expect(route.canDeactivate).toEqual([adminUnsavedChangesGuard]);
    }
  });

  it('keeps both private Dates routes behind the team and unsaved-change guards', () => {
    const routes = (adminPanelRoutes[0].children ?? []).filter((child) =>
      child.path?.startsWith('knowledge/dates'),
    );

    expect(routes.map((route) => route.path)).toEqual(['knowledge/dates', 'knowledge/dates/:id']);
    for (const route of routes) {
      expect(route.canActivate).toEqual([teamGuard]);
      expect(route.canDeactivate).toEqual([adminUnsavedChangesGuard]);
    }
  });
});
