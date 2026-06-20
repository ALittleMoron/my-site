import { Routes } from '@angular/router';
import { adminGuard } from '../../core/auth/auth.guard';

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
        redirectTo: 'articles',
      },
      {
        path: 'articles',
        loadComponent: () =>
          import('./pages/articles-page/articles-page.component').then(
            (m) => m.AdminArticlesPageComponent,
          ),
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
      {
        path: 'workspace/resumes',
        canActivate: [adminGuard],
        loadComponent: () =>
          import('./pages/resumes-page/resumes-page.component').then(
            (m) => m.AdminResumesPageComponent,
          ),
      },
      {
        path: 'workspace/resumes/:id',
        canActivate: [adminGuard],
        loadComponent: () =>
          import('./pages/resume-detail-page/resume-detail-page.component').then(
            (m) => m.AdminResumeDetailPageComponent,
          ),
      },
    ],
  },
];
