import { Routes } from '@angular/router';
import { teamGuard } from '../../core/auth/auth.guard';
import { adminUnsavedChangesGuard } from './guards/admin-unsaved-changes.guard';

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
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/articles-page/articles-page.component').then(
            (m) => m.AdminArticlesPageComponent,
          ),
      },
      {
        path: 'article-folders',
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/article-folders-page/article-folders-page.component').then(
            (m) => m.ArticleFoldersPageComponent,
          ),
      },
      {
        path: 'article-statistics',
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/article-statistics-page/article-statistics-page.component').then(
            (m) => m.AdminArticleStatisticsPageComponent,
          ),
      },
      {
        path: 'articles/:slug',
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/article-detail-page/article-detail-page.component').then(
            (m) => m.AdminArticleDetailPageComponent,
          ),
      },
      {
        path: 'matrix-questions',
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/matrix-questions-page/matrix-questions-page.component').then(
            (m) => m.MatrixQuestionsPageComponent,
          ),
      },
      {
        path: 'matrix-structure',
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/matrix-structure-page/matrix-structure-page.component').then(
            (m) => m.MatrixStructurePageComponent,
          ),
      },
      {
        path: 'matrix-questions/:id',
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/matrix-question-detail-page/matrix-question-detail-page.component').then(
            (m) => m.MatrixQuestionDetailPageComponent,
          ),
      },
      {
        path: 'matrix-question-queue',
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/matrix-question-queue-page/matrix-question-queue-page.component').then(
            (m) => m.MatrixQuestionQueuePageComponent,
          ),
      },
      {
        path: 'workspace/team',
        canActivate: [teamGuard],
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/team-page/team-page.component').then((m) => m.TeamPageComponent),
      },
      {
        path: 'workspace/team/:username',
        canActivate: [teamGuard],
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/team-member-detail-page/team-member-detail-page.component').then(
            (m) => m.TeamMemberDetailPageComponent,
          ),
      },
      {
        path: 'workspace/resumes',
        canActivate: [teamGuard],
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/resumes-page/resumes-page.component').then(
            (m) => m.AdminResumesPageComponent,
          ),
      },
      {
        path: 'workspace/resumes/:id',
        canActivate: [teamGuard],
        canDeactivate: [adminUnsavedChangesGuard],
        loadComponent: () =>
          import('./pages/resume-detail-page/resume-detail-page.component').then(
            (m) => m.AdminResumeDetailPageComponent,
          ),
      },
    ],
  },
];
