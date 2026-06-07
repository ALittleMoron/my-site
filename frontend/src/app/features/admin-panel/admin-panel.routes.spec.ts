import { adminPanelRoutes } from './admin-panel.routes';

describe('adminPanelRoutes', () => {
  it('loads the shell page at the feature root', () => {
    expect(adminPanelRoutes.map((route) => route.path)).toEqual(['']);
    expect(adminPanelRoutes[0].loadComponent).toBeDefined();
    expect(adminPanelRoutes[0].children?.map((route) => route.path)).toEqual([
      '',
      'matrix-question-queue',
    ]);
  });
});
