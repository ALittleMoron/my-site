import { Routes } from '@angular/router';
import { teamGuard } from '../../core/auth/auth.guard';

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
        path: 'articles/:slug',
        loadComponent: () =>
          import('./pages/article-detail-page/article-detail-page.component').then(
            (m) => m.AdminArticleDetailPageComponent,
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
        path: 'matrix-questions/:id',
        loadComponent: () =>
          import('./pages/matrix-question-detail-page/matrix-question-detail-page.component').then(
            (m) => m.MatrixQuestionDetailPageComponent,
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
        path: 'workspace/team',
        canActivate: [teamGuard],
        loadComponent: () =>
          import('./pages/team-page/team-page.component').then((m) => m.TeamPageComponent),
      },
      {
        path: 'workspace/team/:username',
        canActivate: [teamGuard],
        loadComponent: () =>
          import('./pages/team-member-detail-page/team-member-detail-page.component').then(
            (m) => m.TeamMemberDetailPageComponent,
          ),
      },
      {
        path: 'workspace/resumes',
        canActivate: [teamGuard],
        loadComponent: () =>
          import('./pages/resumes-page/resumes-page.component').then(
            (m) => m.AdminResumesPageComponent,
          ),
      },
      {
        path: 'workspace/resumes/:id',
        canActivate: [teamGuard],
        loadComponent: () =>
          import('./pages/resume-detail-page/resume-detail-page.component').then(
            (m) => m.AdminResumeDetailPageComponent,
          ),
      },
    ],
  },
];
