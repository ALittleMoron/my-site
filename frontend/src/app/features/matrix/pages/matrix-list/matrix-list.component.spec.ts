import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { of, throwError, Subject } from 'rxjs';
import { MatrixListComponent } from './matrix-list.component';
import { MatrixService } from '../../services/matrix.service';
import { LayoutPreferencesService } from '../../../../core/layout/layout-preferences.service';
import { AuthService } from '../../../../core/auth/auth.service';
import { ApiError } from '../../../../core/models/api-error.model';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import {
  MatrixQuestionDetail,
  MatrixQuestionList,
  MatrixResource,
} from '../../models/matrix-question.model';
import { NotificationService } from '../../../../core/notifications/notification.service';

const mockQuestionList: MatrixQuestionList = {
  sheet: 'JavaScript',
  sections: [
    {
      section: 'Core',
      subsections: [
        {
          subsection: 'Syntax',
          grades: [
            {
              grade: 'Junior',
              questions: [
                { id: 1, question: 'What is a closure?' },
                { id: 2, question: 'What is hoisting?' },
              ],
            },
          ],
        },
      ],
    },
  ],
};

const mockDetail: MatrixQuestionDetail = {
  id: 1,
  question: 'What is a closure?',
  answer: 'A **closure** is a function.',
  interviewExpectedAnswer: 'Lexical scoping.',
  sheet: 'JavaScript',
  grade: 'Junior',
  section: 'Core',
  subsection: 'Syntax',
  publishStatus: 'Published',
  resources: [],
};

const mockError: ApiError = {
  code: 'server_error',
  type: 'server_error',
  message: 'Internal server error',
  location: null,
  attr: null,
};

describe('MatrixListComponent', () => {
  let fixture: ComponentFixture<MatrixListComponent>;
  let component: MatrixListComponent;
  let matrixService: {
    getSheets: jest.Mock;
    getQuestions: jest.Mock;
    getQuestion: jest.Mock;
    searchResources: jest.Mock;
    createQuestion: jest.Mock;
    updateQuestion: jest.Mock;
    publishQuestion: jest.Mock;
    unpublishQuestion: jest.Mock;
    deleteQuestion: jest.Mock;
  };
  let layoutPreferences: {
    matrixLayout: ReturnType<typeof import('@angular/core').signal<'list' | 'grid'>>;
    setMatrixLayout: jest.Mock;
  };
  let authService: {
    isAdmin: ReturnType<typeof import('@angular/core').computed<boolean>>;
  };
  let isAdminSignal: ReturnType<typeof import('@angular/core').signal<boolean>>;
  let notificationService: { success: jest.Mock; error: jest.Mock };

  beforeEach(async () => {
    matrixService = {
      getSheets: jest.fn().mockReturnValue(of(['JavaScript', 'Python'])),
      getQuestions: jest.fn().mockReturnValue(of(mockQuestionList)),
      getQuestion: jest.fn().mockReturnValue(of(mockDetail)),
      searchResources: jest.fn().mockReturnValue(of([])),
      createQuestion: jest.fn().mockReturnValue(of(mockDetail)),
      updateQuestion: jest.fn().mockReturnValue(of(mockDetail)),
      publishQuestion: jest.fn().mockReturnValue(of(undefined)),
      unpublishQuestion: jest.fn().mockReturnValue(of(undefined)),
      deleteQuestion: jest.fn().mockReturnValue(of(undefined)),
    };

    const { signal, computed } = await import('@angular/core');
    const layoutSignal = signal<'list' | 'grid'>('list');
    layoutPreferences = {
      matrixLayout: layoutSignal,
      setMatrixLayout: jest.fn((mode: 'list' | 'grid') => layoutSignal.set(mode)),
    };

    isAdminSignal = signal(false);
    authService = {
      isAdmin: computed(() => isAdminSignal()),
    };
    notificationService = {
      success: jest.fn(),
      error: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [MatrixListComponent],
      providers: [
        { provide: MatrixService, useValue: matrixService },
        { provide: LayoutPreferencesService, useValue: layoutPreferences },
        { provide: AuthService, useValue: authService },
        { provide: NotificationService, useValue: notificationService },
        provideI18nTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixListComponent);
    component = fixture.componentInstance;
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should show loading spinner while loading', () => {
    // Initialize first, then override with our desired state
    fixture.detectChanges();
    component.loading.set(true);
    component.error.set(null);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-loading-spinner')).toBeTruthy();
  });

  it('should not show spinner when not loading', () => {
    fixture.detectChanges();
    component.loading.set(false);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-loading-spinner')).toBeFalsy();
  });

  it('should show error message when error is set', () => {
    fixture.detectChanges();
    component.loading.set(false);
    component.error.set(mockError);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-error-message')).toBeTruthy();
  });

  it('should show empty state when no questions match filter', () => {
    fixture.detectChanges();
    component.loading.set(false);
    component.error.set(null);
    component.questions.set({ sheet: 'JavaScript', sections: [] });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-empty-state')).toBeTruthy();
  });

  it('should load sheets on init and auto-select first sheet', () => {
    fixture.detectChanges();
    expect(matrixService.getSheets).toHaveBeenCalled();
    expect(component.selectedSheet()).toBe('JavaScript');
  });

  it('should restore sheet from localStorage on init', () => {
    localStorage.setItem('chosenSheet', 'Python');
    // Create a new component instance so ngOnInit reads localStorage
    fixture = TestBed.createComponent(MatrixListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    const tabs = fixture.nativeElement.querySelectorAll('app-matrix-sheet-tabs button');
    const pythonTab = Array.from(tabs).find(
      (btn: unknown) => (btn as HTMLElement).textContent?.trim() === 'Python',
    ) as HTMLElement | undefined;
    expect(pythonTab).toBeTruthy();
    expect(pythonTab!.classList).toContain('button-active');
  });

  it('should store sheet to localStorage when sheet is selected', () => {
    fixture.detectChanges();
    component.selectSheet('Python');
    expect(localStorage.getItem('chosenSheet')).toBe('Python');
  });

  it('should load questions for selected sheet', () => {
    fixture.detectChanges();
    component.selectSheet('Python');
    expect(matrixService.getQuestions).toHaveBeenCalledWith('Python', true);
  });

  it('should render list layout by default', () => {
    component.loading.set(false);
    component.error.set(null);
    component.questions.set(mockQuestionList);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-matrix-grouped-list')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('app-matrix-grouped-grid')).toBeFalsy();
  });

  it('should render Russian page title', () => {
    fixture.detectChanges();
    const title = fixture.nativeElement.querySelector('h1') as HTMLElement;
    expect(title.textContent?.trim()).toBe('Матрица компетенций');
  });

  it('should not show published/all filter for non-admin users', () => {
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('#onlyPublishedToggle')).toBeNull();
  });

  it('should show published/all filter for admin users', () => {
    isAdminSignal.set(true);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('#onlyPublishedToggle')).not.toBeNull();
  });

  it('should render grid layout when layoutMode is grid', () => {
    component.loading.set(false);
    component.error.set(null);
    component.questions.set(mockQuestionList);
    layoutPreferences.matrixLayout.set('grid');
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-matrix-grouped-grid')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('app-matrix-grouped-list')).toBeFalsy();
  });

  it('should filter questions by search term, removing empty groups', () => {
    component.questions.set(mockQuestionList);
    component.search.set('closure');
    const filtered = component.filteredQuestions();
    expect(filtered).not.toBeNull();
    const allQuestions = filtered!.sections.flatMap((s) =>
      s.subsections.flatMap((sub) => sub.grades.flatMap((g) => g.questions)),
    );
    expect(allQuestions.length).toBe(1);
    expect(allQuestions[0].question).toBe('What is a closure?');
  });

  it('should remove empty grade groups when filtering', () => {
    component.questions.set(mockQuestionList);
    component.search.set('nonexistent');
    const filtered = component.filteredQuestions();
    expect(filtered!.sections.length).toBe(0);
  });

  it('should handle empty sheet list gracefully', () => {
    matrixService.getSheets.mockReturnValue(of([]));
    fixture = TestBed.createComponent(MatrixListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-loading-spinner')).toBeFalsy();
    expect(fixture.nativeElement.querySelector('app-matrix-sheet-tabs')).toBeFalsy();
    expect(fixture.nativeElement.querySelector('app-empty-state')).toBeTruthy();
  });

  it('should show error when getSheets fails', () => {
    matrixService.getSheets.mockReturnValue(throwError(() => mockError));
    // Create new component instance so ngOnInit runs with new mock
    fixture = TestBed.createComponent(MatrixListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-error-message')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('app-loading-spinner')).toBeFalsy();
  });

  it('should open detail modal when openDetail is called', () => {
    fixture.detectChanges();
    component.loading.set(false);
    component.error.set(null);
    component.questions.set(mockQuestionList);
    fixture.detectChanges();
    component.openDetail(1);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-matrix-question-detail')).toBeTruthy();
  });

  it('should set detailLoading when loading a question', () => {
    const subject = new Subject();
    matrixService.getQuestion.mockReturnValue(subject.asObservable());
    fixture.detectChanges();
    component.openDetail(1);
    fixture.detectChanges();
    const modal = fixture.nativeElement.querySelector('[role="dialog"]');
    expect(modal).toBeTruthy();
    expect(modal.querySelector('app-loading-spinner')).toBeTruthy();
  });

  it('should set selectedQuestion after detail loads', () => {
    fixture.detectChanges();
    component.openDetail(1);
    fixture.detectChanges();
    const modal = fixture.nativeElement.querySelector('[role="dialog"]');
    expect(modal).toBeTruthy();
    expect(modal.querySelector('app-loading-spinner')).toBeFalsy();
    expect(modal.querySelector('app-matrix-question-detail .question-detail')).toBeTruthy();
  });

  it('should set detailError when detail load fails', () => {
    matrixService.getQuestion.mockReturnValue(throwError(() => mockError));
    fixture.detectChanges();
    component.openDetail(1);
    fixture.detectChanges();
    const modal = fixture.nativeElement.querySelector('[role="dialog"]');
    expect(modal).toBeTruthy();
    expect(modal.querySelector('app-error-message')).toBeTruthy();
    expect(modal.querySelector('app-loading-spinner')).toBeFalsy();
  });

  it('uses latest resource search response when requests resolve out of order', fakeAsync(() => {
    const first = new Subject<MatrixResource[]>();
    const second = new Subject<MatrixResource[]>();
    matrixService.searchResources
      .mockReturnValueOnce(first.asObservable())
      .mockReturnValueOnce(second.asObservable());

    fixture.detectChanges();
    component.searchResources('py');
    tick(250);
    component.searchResources('pyd');
    tick(250);

    second.next([{ id: 2, name: 'Pydantic', url: 'https://docs.pydantic.dev' }]);
    second.complete();
    first.next([{ id: 1, name: 'Python', url: 'https://docs.python.org' }]);
    first.complete();

    expect(component.resourceSearchResults()).toEqual([
      { id: 2, name: 'Pydantic', url: 'https://docs.pydantic.dev' },
    ]);
  }));

  it('searches resources with trimmed query', fakeAsync(() => {
    fixture.detectChanges();

    component.searchResources('  pydantic  ');
    tick(250);

    expect(matrixService.searchResources).toHaveBeenCalledWith('pydantic', 10);
  }));

  it('clears resource search results when latest search fails', fakeAsync(() => {
    matrixService.searchResources
      .mockReturnValueOnce(of([{ id: 1, name: 'Python', url: 'https://docs.python.org' }]))
      .mockReturnValueOnce(throwError(() => mockError));

    fixture.detectChanges();
    component.searchResources('python');
    tick(250);
    expect(component.resourceSearchResults()).toEqual([
      { id: 1, name: 'Python', url: 'https://docs.python.org' },
    ]);

    component.searchResources('pydantic');
    tick(250);

    expect(component.resourceSearchResults()).toEqual([]);
    expect(component.error()).toBeNull();
  }));

  it('should hide modal and clear question when closeDetail is called', () => {
    fixture.detectChanges();
    component.openDetail(1);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role="dialog"]')).toBeTruthy();
    component.closeDetail();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role="dialog"]')).toBeFalsy();
  });

  it('should call publishQuestion and reload questions on onPublish', () => {
    fixture.detectChanges();
    component.selectedSheet.set('JavaScript');
    component.onPublish(1);
    expect(matrixService.publishQuestion).toHaveBeenCalledWith(1);
    expect(matrixService.getQuestions).toHaveBeenCalledWith('JavaScript', true);
    expect(notificationService.success).toHaveBeenCalledWith('Вопрос опубликован.');
  });

  it('should call unpublishQuestion and reload questions on onUnpublish', () => {
    fixture.detectChanges();
    component.selectedSheet.set('JavaScript');
    component.onUnpublish(1);
    expect(matrixService.unpublishQuestion).toHaveBeenCalledWith(1);
    expect(matrixService.getQuestions).toHaveBeenCalledWith('JavaScript', true);
    expect(notificationService.success).toHaveBeenCalledWith('Вопрос снят с публикации.');
  });

  it('should call deleteQuestion, close detail, and reload questions on onDelete', () => {
    fixture.detectChanges();
    component.openDetail(1);
    fixture.detectChanges();
    component.selectedSheet.set('JavaScript');
    component.onDelete(1);
    fixture.detectChanges();
    expect(matrixService.deleteQuestion).toHaveBeenCalledWith(1);
    expect(fixture.nativeElement.querySelector('[role="dialog"]')).toBeFalsy();
    expect(matrixService.getQuestions).toHaveBeenCalledWith('JavaScript', true);
    expect(notificationService.success).toHaveBeenCalledWith('Вопрос удалён.');
  });

  it('should set error when publishQuestion fails', () => {
    fixture.detectChanges();
    matrixService.publishQuestion.mockReturnValue(throwError(() => mockError));
    component.onPublish(1);
    expect(component.error()).toEqual(mockError);
    expect(notificationService.error).toHaveBeenCalledWith('Не удалось опубликовать вопрос.');
  });

  it('should set error when unpublishQuestion fails', () => {
    fixture.detectChanges();
    matrixService.unpublishQuestion.mockReturnValue(throwError(() => mockError));
    component.onUnpublish(1);
    expect(component.error()).toEqual(mockError);
    expect(notificationService.error).toHaveBeenCalledWith('Не удалось снять вопрос с публикации.');
  });

  it('should set error when deleteQuestion fails', () => {
    fixture.detectChanges();
    matrixService.deleteQuestion.mockReturnValue(throwError(() => mockError));
    component.onDelete(1);
    expect(component.error()).toEqual(mockError);
    expect(notificationService.error).toHaveBeenCalledWith('Не удалось удалить вопрос.');
  });
});
