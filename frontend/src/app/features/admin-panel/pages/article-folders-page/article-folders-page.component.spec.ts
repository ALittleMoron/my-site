import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CdkDragDrop } from '@angular/cdk/drag-drop';
import { of, throwError } from 'rxjs';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { ArticleFolder } from '../../models/article-workspace.model';
import { ArticleWorkspaceService } from '../../services/article-workspace.service';
import { ArticleFoldersPageComponent } from './article-folders-page.component';

describe('ArticleFoldersPageComponent', () => {
  let fixture: ComponentFixture<ArticleFoldersPageComponent>;
  let articlesService: {
    getFolders: jest.Mock;
    updateFolderPriorities: jest.Mock;
  };
  let notifications: {
    success: jest.Mock;
    error: jest.Mock;
  };

  beforeEach(async () => {
    articlesService = {
      getFolders: jest.fn().mockReturnValue(of([folder('folder-1', 'Engineering', 1)])),
      updateFolderPriorities: jest.fn().mockReturnValue(of(undefined)),
    };
    notifications = {
      success: jest.fn(),
      error: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [ArticleFoldersPageComponent],
      providers: [
        { provide: ArticleWorkspaceService, useValue: articlesService },
        { provide: NotificationService, useValue: notifications },
        provideI18nTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ArticleFoldersPageComponent);
    fixture.detectChanges();
  });

  it('renders loaded folders', () => {
    expect(articlesService.getFolders).toHaveBeenCalledWith('ru');
    expect(fixture.nativeElement.textContent).toContain('Engineering');
    expect(fixture.nativeElement.textContent).toContain('engineering');
  });

  it('reorders folders and saves ordered ids', () => {
    articlesService.getFolders.mockReturnValue(
      of([folder('folder-1', 'Engineering', 1), folder('folder-2', 'Architecture', 2)]),
    );
    fixture.componentInstance.loadFolders();
    fixture.detectChanges();

    fixture.componentInstance.dropFolders(dropEvent(1, 0));
    fixture.detectChanges();

    expect(articlesService.updateFolderPriorities).toHaveBeenCalledWith(['folder-2', 'folder-1']);
    expect(
      fixture.componentInstance.folders().map((item) => `${item.id}:${item.priority}`),
    ).toEqual(['folder-2:1', 'folder-1:2']);
    expect(notifications.success).toHaveBeenCalledWith('Порядок папок сохранён.');
  });

  it('rolls back and reloads when reorder fails', () => {
    articlesService.getFolders.mockReturnValue(
      of([folder('folder-1', 'Engineering', 1), folder('folder-2', 'Architecture', 2)]),
    );
    articlesService.updateFolderPriorities.mockReturnValue(throwError(() => new Error('Nope')));
    fixture.componentInstance.loadFolders();
    fixture.detectChanges();

    fixture.componentInstance.dropFolders(dropEvent(1, 0));
    fixture.detectChanges();

    expect(fixture.componentInstance.folders().map((item) => item.id)).toEqual([
      'folder-1',
      'folder-2',
    ]);
    expect(notifications.error).toHaveBeenCalledWith('Не удалось сохранить порядок папок.');
    expect(articlesService.getFolders).toHaveBeenCalledTimes(3);
  });
});

function dropEvent(previousIndex: number, currentIndex: number): CdkDragDrop<ArticleFolder[]> {
  return { previousIndex, currentIndex } as CdkDragDrop<ArticleFolder[]>;
}

function folder(id: string, name: string, priority: number): ArticleFolder {
  return {
    id,
    key: name.toLowerCase(),
    name,
    priority,
    translations: {
      ru: { name },
      en: { name },
    },
  };
}
