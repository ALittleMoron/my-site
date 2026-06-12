import { Routes } from '@angular/router';

export const adminPanelRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/admin-panel-page/admin-panel-page.component').then(
        (m) => m.AdminPanelPageComponent,
      ),
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'matrix-questions',
      },
      {
        path: 'matrix-questions',
        loadComponent: () =>
          import('./pages/matrix-questions-page/matrix-questions-page.component').then(
            (m) => m.MatrixQuestionsPageComponent,
          ),
      },
      {
        path: 'matrix-question-queue',
        loadComponent: () =>
          import('./pages/matrix-question-queue-page/matrix-question-queue-page.component').then(
            (m) => m.MatrixQuestionQueuePageComponent,
          ),
      },
    ],
  },
];
