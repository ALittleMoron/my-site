import { CdkDragDrop } from '@angular/cdk/drag-drop';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Subject, of, throwError } from 'rxjs';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { AdminMatrixStructure } from '../../models/matrix-question-workspace.model';
import { MatrixQuestionWorkspaceService } from '../../services/matrix-question-workspace.service';
import { MatrixStructurePageComponent } from './matrix-structure-page.component';

describe('MatrixStructurePageComponent', () => {
  let fixture: ComponentFixture<MatrixStructurePageComponent>;
  let service: jest.Mocked<MatrixQuestionWorkspaceService>;
  let notifications: { success: jest.Mock; error: jest.Mock };

  beforeEach(async () => {
    service = {
      getStructure: jest.fn().mockReturnValue(of(matrixStructure())),
      updateSheetPriorities: jest.fn().mockReturnValue(of(undefined)),
      updateSectionPriorities: jest.fn().mockReturnValue(of(undefined)),
      updateSubsectionPriorities: jest.fn().mockReturnValue(of(undefined)),
    } as unknown as jest.Mocked<MatrixQuestionWorkspaceService>;
    notifications = {
      success: jest.fn(),
      error: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [MatrixStructurePageComponent],
      providers: [
        provideI18nTesting(),
        { provide: MatrixQuestionWorkspaceService, useValue: service },
        { provide: NotificationService, useValue: notifications },
      ],
    }).compileComponents();
  });

  it('renders loading and then the loaded structure', () => {
    const structure = new Subject<AdminMatrixStructure>();
    service.getStructure.mockReturnValue(structure.asObservable());

    createComponent();

    const loadingSpinner = fixture.nativeElement.querySelector('app-loading-spinner');
    expect(loadingSpinner).toBeTruthy();

    structure.next(matrixStructure());
    structure.complete();
    fixture.detectChanges();

    expect(service.getStructure).toHaveBeenCalledWith('ru');
    expect(fixture.nativeElement.textContent).toContain('Питон');
    expect(fixture.nativeElement.textContent).toContain('Основы');
    expect(fixture.nativeElement.textContent).toContain('Стиль');
  });

  it('uses the visible blocks as drag targets without priority action buttons', () => {
    createComponent();

    expect(
      fixture.nativeElement.querySelector('.matrix-structure-sheet-item.cdk-drag'),
    ).toBeTruthy();
    expect(fixture.nativeElement.querySelector('.matrix-structure-section.cdk-drag')).toBeTruthy();
    expect(
      fixture.nativeElement.querySelector('.matrix-structure-subsection.cdk-drag'),
    ).toBeTruthy();
    expect(fixture.nativeElement.querySelector('.matrix-structure-icon-button')).toBeNull();
    expect(fixture.nativeElement.querySelector('[title="Перетащить"]')).toBeNull();
    expect(fixture.nativeElement.querySelector('[title="Переместить выше"]')).toBeNull();
    expect(fixture.nativeElement.querySelector('[title="Переместить ниже"]')).toBeNull();
  });

  it('autosaves sheet drag-drop reorder optimistically', () => {
    createComponent();

    fixture.componentInstance.dropSheets(dropEvent(0, 1));
    fixture.detectChanges();

    expect(service.updateSheetPriorities).toHaveBeenCalledWith([2, 1]);
    expect(notifications.success).toHaveBeenCalledWith('Порядок структуры сохранён.');
    const tabs = sheetTabs();
    expect(tabs.map((tab) => tab.textContent?.trim())).toEqual(['SQL', 'Питон']);
  });

  it('does not autosave same-position drops', () => {
    createComponent();

    fixture.componentInstance.dropSheets(dropEvent(0, 0));

    expect(service.updateSheetPriorities).not.toHaveBeenCalled();
  });

  it('rolls back and reloads structure when autosave fails', () => {
    service.updateSheetPriorities.mockReturnValue(throwError(() => ({ message: 'Failed' })));
    createComponent();

    fixture.componentInstance.dropSheets(dropEvent(0, 1));
    fixture.detectChanges();

    expect(notifications.error).toHaveBeenCalledWith('Не удалось сохранить порядок структуры.');
    expect(service.getStructure).toHaveBeenCalledTimes(2);
    expect(sheetTabs().map((tab) => tab.textContent?.trim())).toEqual(['Питон', 'SQL']);
  });

  it('autosaves nested section and subsection reorders', () => {
    createComponent();
    const sheet = fixture.componentInstance.structure().sheets[0];
    const section = sheet.sections[0];

    fixture.componentInstance.dropSections(dropEvent(0, 1), sheet);
    fixture.componentInstance.dropSubsections(dropEvent(0, 1), section);

    expect(service.updateSectionPriorities).toHaveBeenCalledWith(1, [3, 2]);
    expect(service.updateSubsectionPriorities).toHaveBeenCalledWith(2, [5, 4]);
  });

  function createComponent(): void {
    fixture = TestBed.createComponent(MatrixStructurePageComponent);
    fixture.detectChanges();
  }

  function sheetTabs(): HTMLButtonElement[] {
    return Array.from(
      fixture.nativeElement.querySelectorAll('[data-testid="matrix-structure-sheet-tab"]'),
    );
  }
});

function dropEvent<T>(previousIndex: number, currentIndex: number): CdkDragDrop<T> {
  return { previousIndex, currentIndex } as CdkDragDrop<T>;
}

function matrixStructure(): AdminMatrixStructure {
  return {
    sheets: [
      {
        id: 1,
        key: 'python',
        name: 'Питон',
        priority: 1,
        translations: { ru: { name: 'Питон' }, en: { name: 'Python' } },
        sections: [
          {
            id: 2,
            name: 'Основы',
            priority: 1,
            translations: { ru: { name: 'Основы' }, en: { name: 'Core' } },
            subsections: [
              {
                id: 4,
                name: 'Стиль',
                priority: 1,
                translations: { ru: { name: 'Стиль' }, en: { name: 'Style' } },
              },
              {
                id: 5,
                name: 'Типизация',
                priority: 2,
                translations: { ru: { name: 'Типизация' }, en: { name: 'Typing' } },
              },
            ],
          },
          {
            id: 3,
            name: 'Продвинутое',
            priority: 2,
            translations: { ru: { name: 'Продвинутое' }, en: { name: 'Advanced' } },
            subsections: [],
          },
        ],
      },
      {
        id: 2,
        key: 'sql',
        name: 'SQL',
        priority: 2,
        translations: { ru: { name: 'SQL' }, en: { name: 'SQL' } },
        sections: [],
      },
    ],
  };
}
