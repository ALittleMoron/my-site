import { AdminPanelNavigationSection } from './models/admin-panel-navigation.model';

export const ADMIN_PANEL_NAVIGATION_SECTIONS: readonly AdminPanelNavigationSection[] = [
  {
    key: 'matrix',
    labelKey: 'shell.nav.matrix',
    pages: [
      {
        key: 'matrix-question-queue',
        labelKey: 'adminPanel.section.matrixQuestionQueue',
        route: '/admin-panel/matrix-question-queue',
        badgeTextKey: null,
      },
    ],
  },
];
