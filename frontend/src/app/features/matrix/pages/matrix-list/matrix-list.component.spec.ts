import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { MatrixListComponent } from './matrix-list.component';
import { MatrixService } from '../../services/matrix.service';
import { ApiError } from '../../../../core/models/api-error.model';
import { MatrixQuestion } from '../../models/matrix-question.model';

const mockQuestion: MatrixQuestion = {
  id: '1',
  title: 'What is a closure?',
  description: 'Explain JS closures.',
  grade: 'junior',
  topic: 'JavaScript',
  is_published: true,
};

const mockError: ApiError = {
  code: 'server_error',
  type: 'server_error',
  message: 'Internal server error',
  location: null,
  attr: null,
};

const activatedRouteStub = {
  snapshot: { queryParamMap: { get: () => null } },
};

describe('MatrixListComponent', () => {
  let fixture: ComponentFixture<MatrixListComponent>;
  let component: MatrixListComponent;
  let matrixService: { getQuestions: jest.Mock };

  beforeEach(async () => {
    matrixService = { getQuestions: jest.fn().mockReturnValue(of([])) };

    await TestBed.configureTestingModule({
      imports: [MatrixListComponent],
      providers: [
        provideRouter([]),
        { provide: MatrixService, useValue: matrixService },
        { provide: ActivatedRoute, useValue: activatedRouteStub },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixListComponent);
    component = fixture.componentInstance;
  });

  it('should show loading spinner while loading', () => {
    component.loading.set(true);
    component.error.set(null);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-loading-spinner')).toBeTruthy();
  });

  it('should not show spinner when not loading', () => {
    component.loading.set(false);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-loading-spinner')).toBeFalsy();
  });

  it('should show error message when error is set', () => {
    component.loading.set(false);
    component.error.set(mockError);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-error-message')).toBeTruthy();
  });

  it('should show empty state when questions list is empty', () => {
    component.loading.set(false);
    component.error.set(null);
    component.questions.set([]);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-empty-state')).toBeTruthy();
  });

  it('should show question cards when questions are loaded', () => {
    component.loading.set(false);
    component.error.set(null);
    component.questions.set([mockQuestion]);
    fixture.detectChanges();
    expect(
      fixture.nativeElement.querySelectorAll('app-matrix-question-card').length,
    ).toBe(1);
  });

  it('should toggle layout mode between list and grid', () => {
    expect(component.layoutMode()).toBe('list');
    component.toggleLayout();
    expect(component.layoutMode()).toBe('grid');
    component.toggleLayout();
    expect(component.layoutMode()).toBe('list');
  });

  it('should call getQuestions with search value after debounce', fakeAsync(() => {
    fixture.detectChanges();
    component.searchControl.setValue('closure');
    tick(300);
    expect(matrixService.getQuestions).toHaveBeenCalledWith('closure');
  }));
});
