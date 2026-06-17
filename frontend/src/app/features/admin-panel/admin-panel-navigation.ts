import { AdminPanelNavigationSection } from './models/admin-panel-navigation.model';

export const ADMIN_PANEL_NAVIGATION_SECTIONS: readonly AdminPanelNavigationSection[] = [
  {
    key: 'articles',
    labelKey: 'adminPanel.section.articles',
    pages: [
      {
        key: 'articles',
        labelKey: 'shell.nav.articles',
        route: '/admin-panel/articles',
        badgeTextKey: null,
      },
    ],
  },
  {
    key: 'matrix',
    labelKey: 'shell.nav.matrix',
    pages: [
      {
        key: 'matrix-questions',
        labelKey: 'adminPanel.section.matrixQuestions',
        route: '/admin-panel/matrix-questions',
        badgeTextKey: null,
      },
      {
        key: 'matrix-question-queue',
        labelKey: 'adminPanel.section.matrixQuestionQueue',
        route: '/admin-panel/matrix-question-queue',
        badgeTextKey: null,
      },
    ],
  },
];
