import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { ApiError } from '../../../../core/models/api-error.model';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { Resume, Resumes, ResumePayload } from '../../models/resume-workspace.model';
import { ResumeWorkspaceService } from '../../services/resume-workspace.service';
import { AdminResumesPageComponent } from './resumes-page.component';

describe('AdminResumesPageComponent', () => {
  let fixture: ComponentFixture<AdminResumesPageComponent>;
  let service: {
    listResumes: jest.Mock;
    createResume: jest.Mock;
  };
  let router: Router;
  let notifications: {
    success: jest.Mock;
    error: jest.Mock;
  };

  beforeEach(async () => {
    service = {
      listResumes: jest.fn().mockReturnValue(of(resumesList([resume()]))),
      createResume: jest.fn().mockReturnValue(of(resume())),
    };
    notifications = {
      success: jest.fn(),
      error: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [AdminResumesPageComponent],
      providers: [
        provideRouter([]),
        provideI18nTesting(),
        { provide: ResumeWorkspaceService, useValue: service },
        { provide: NotificationService, useValue: notifications },
      ],
    }).compileComponents();

    router = TestBed.inject(Router);
    jest.spyOn(router, 'navigateByUrl').mockResolvedValue(true);
    fixture = TestBed.createComponent(AdminResumesPageComponent);
    fixture.detectChanges();
  });

  it('loads the resume list', () => {
    expect(service.listResumes).toHaveBeenCalledWith({ page: 1, pageSize: 20 });
    expect(fixture.nativeElement.textContent).toContain('Backend resume');
    expect(fixture.nativeElement.textContent).toContain('EN');
    expect(fixture.nativeElement.textContent).toContain('2026-01-02');
    expect(fixture.nativeElement.textContent).toContain('2026-01-01');
  });

  it('shows an empty state', () => {
    service.listResumes.mockReturnValue(of(resumesList([])));

    fixture.componentInstance.loadResumes();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Резюме пока не созданы.');
  });

  it('opens the create dialog', () => {
    const button = fixture.nativeElement.querySelector(
      '[data-testid="resume-create-open"]',
    ) as HTMLButtonElement;

    button.click();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="resume-create-dialog"]')).not.toBe(
      null,
    );
  });

  it('creates a resume and navigates to detail', () => {
    fixture.componentInstance.openCreateDialog();
    fixture.detectChanges();

    setInputValue('resume-create-title', 'Target resume');
    setInputValue('resume-create-language', 'en');
    setInputValue('resume-create-full-name', 'Dmitriy');
    setInputValue('resume-create-role', 'Backend engineer');
    setInputValue('resume-create-summary', 'Summary');

    const form = fixture.nativeElement.querySelector(
      '[data-testid="resume-create-form"]',
    ) as HTMLFormElement;
    form.dispatchEvent(new Event('submit'));
    fixture.detectChanges();

    expect(service.createResume).toHaveBeenCalledWith({
      title: 'Target resume',
      language: 'en',
      content: expect.objectContaining({
        profile: expect.objectContaining({
          fullName: 'Dmitriy',
          role: 'Backend engineer',
          phone: '',
        }),
        summary: {
          text: 'Summary',
        },
        skills: [],
        experience: [],
      }),
    } satisfies ResumePayload);
    expect(notifications.success).toHaveBeenCalledWith('Резюме сохранено.');
    expect(router.navigateByUrl).toHaveBeenCalledWith('/admin-panel/workspace/resumes/7');
  });

  it('marks required create fields and clears red border after a required value is entered', () => {
    fixture.componentInstance.openCreateDialog();
    fixture.detectChanges();

    const title = fixture.nativeElement.querySelector(
      '[data-testid="resume-create-title"]',
    ) as HTMLInputElement;
    const form = fixture.nativeElement.querySelector(
      '[data-testid="resume-create-form"]',
    ) as HTMLFormElement;

    expect(fixture.nativeElement.textContent).toContain('Название *');

    form.dispatchEvent(new Event('submit'));
    fixture.detectChanges();

    expect(title.classList).toContain('is-invalid');
    expect(service.createResume).not.toHaveBeenCalled();

    title.value = 'Target resume';
    title.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(title.classList).not.toContain('is-invalid');
  });

  it('requires choosing a resume language before creation', () => {
    fixture.componentInstance.openCreateDialog();
    fixture.detectChanges();

    setInputValue('resume-create-title', 'Target resume');
    setInputValue('resume-create-full-name', 'Dmitriy');
    setInputValue('resume-create-role', 'Backend engineer');
    setInputValue('resume-create-summary', 'Summary');

    const language = fixture.nativeElement.querySelector(
      '[data-testid="resume-create-language"]',
    ) as HTMLSelectElement;
    const form = fixture.nativeElement.querySelector(
      '[data-testid="resume-create-form"]',
    ) as HTMLFormElement;
    form.dispatchEvent(new Event('submit'));
    fixture.detectChanges();

    expect(language.classList).toContain('is-invalid');
    expect(service.createResume).not.toHaveBeenCalled();
  });

  it('shows an API error notification on create failure', () => {
    service.createResume.mockReturnValue(throwError(() => apiError()));
    fixture.componentInstance.openCreateDialog();
    fixture.detectChanges();

    setInputValue('resume-create-title', 'Target resume');
    setInputValue('resume-create-language', 'en');
    setInputValue('resume-create-full-name', 'Dmitriy');
    setInputValue('resume-create-role', 'Backend engineer');
    setInputValue('resume-create-summary', 'Summary');

    fixture.componentInstance.createResume();
    fixture.detectChanges();

    expect(notifications.error).toHaveBeenCalledWith('Не удалось сохранить резюме.');
  });

  function setInputValue(testId: string, value: string): void {
    const input = fixture.nativeElement.querySelector(`[data-testid="${testId}"]`) as
      | HTMLInputElement
      | HTMLTextAreaElement
      | HTMLSelectElement;
    input.value = value;
    input.dispatchEvent(new Event('input'));
    input.dispatchEvent(new Event('change'));
  }
});

function resumesList(resumes: Resume[]): Resumes {
  return {
    totalCount: resumes.length,
    totalPages: resumes.length > 0 ? 1 : 0,
    resumes,
  };
}

function resume(): Resume {
  return {
    id: 7,
    title: 'Backend resume',
    language: 'en',
    createdAt: '2026-01-01T03:04:05+00:00',
    updatedAt: '2026-01-02T03:04:05+00:00',
    content: {
      profile: {
        fullName: 'Candidate Name',
        role: 'Engineer',
        location: '',
        email: '',
        phone: '',
        websiteUrl: '',
        linkedinUrl: '',
        githubUrl: '',
        telegram: '',
      },
      summary: {
        text: 'Short experience summary.',
      },
      skills: [],
      experience: [],
      education: [],
      languages: [],
      certifications: [],
      additionalSections: [],
    },
  };
}

function apiError(): ApiError {
  return {
    code: 'bad_request',
    type: 'BadRequest',
    message: 'Bad request',
    location: null,
    attr: null,
  };
}
