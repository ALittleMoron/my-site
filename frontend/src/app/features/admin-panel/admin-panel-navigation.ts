import { AdminPanelNavigationSection } from './models/admin-panel-navigation.model';

export const ADMIN_PANEL_NAVIGATION_SECTIONS: readonly AdminPanelNavigationSection[] = [
  {
    key: 'workspace',
    labelKey: 'adminPanel.section.workspace',
    pages: [
      {
        key: 'team',
        labelKey: 'adminPanel.section.team',
        route: '/admin-panel/workspace/team',
        badgeTextKey: null,
        adminOnly: true,
      },
      {
        key: 'resumes',
        labelKey: 'adminPanel.section.resumes',
        route: '/admin-panel/workspace/resumes',
        badgeTextKey: null,
        adminOnly: true,
      },
    ],
  },
  {
    key: 'articles',
    labelKey: 'adminPanel.section.articles',
    pages: [
      {
        key: 'articles',
        labelKey: 'shell.nav.articles',
        route: '/admin-panel/articles',
        badgeTextKey: null,
        adminOnly: false,
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
        adminOnly: false,
      },
      {
        key: 'matrix-question-queue',
        labelKey: 'adminPanel.section.matrixQuestionQueue',
        route: '/admin-panel/matrix-question-queue',
        badgeTextKey: null,
        adminOnly: false,
      },
    ],
  },
];
