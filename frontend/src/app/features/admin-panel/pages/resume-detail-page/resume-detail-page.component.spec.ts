import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router, provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { ApiError } from '../../../../core/models/api-error.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { Resume, ResumePayload } from '../../models/resume-workspace.model';
import { ResumeWorkspaceService } from '../../services/resume-workspace.service';
import { AdminResumeDetailPageComponent } from './resume-detail-page.component';

describe('AdminResumeDetailPageComponent', () => {
  let fixture: ComponentFixture<AdminResumeDetailPageComponent>;
  let service: {
    getResume: jest.Mock;
    updateResume: jest.Mock;
    deleteResume: jest.Mock;
  };
  let router: Router;
  let i18n: I18nService;
  let notifications: {
    success: jest.Mock;
    error: jest.Mock;
  };

  beforeEach(async () => {
    service = {
      getResume: jest.fn().mockReturnValue(of(resume())),
      updateResume: jest.fn().mockReturnValue(of(resume({ title: 'Updated resume' }))),
      deleteResume: jest.fn().mockReturnValue(of(undefined)),
    };
    notifications = {
      success: jest.fn(),
      error: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [AdminResumeDetailPageComponent],
      providers: [
        provideRouter([]),
        provideI18nTesting(),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: (key: string) => (key === 'id' ? '7' : null),
              },
            },
          },
        },
        { provide: ResumeWorkspaceService, useValue: service },
        { provide: NotificationService, useValue: notifications },
      ],
    }).compileComponents();

    router = TestBed.inject(Router);
    i18n = TestBed.inject(I18nService);
    jest.spyOn(router, 'navigateByUrl').mockResolvedValue(true);
    fixture = TestBed.createComponent(AdminResumeDetailPageComponent);
    fixture.detectChanges();
  });

  it('loads detail into the edit form', () => {
    expect(service.getResume).toHaveBeenCalledWith(7);
    expect(inputValue('resume-title')).toBe('Backend resume');
    expect(inputValue('resume-profile-full-name')).toBe('Candidate Name');
    fixture.componentInstance.setActiveTab('summary');
    fixture.detectChanges();
    expect(inputValue('resume-summary-ru')).toBe('Сильный backend опыт.');
    expect(fixture.nativeElement.textContent).toContain('Профиль');
    expect(fixture.nativeElement.textContent).toContain('Навыки');
  });

  it('edits and saves an explicit update payload', () => {
    setInputValue('resume-title', 'Target backend resume');
    fixture.componentInstance.setActiveTab('summary');
    fixture.detectChanges();
    setInputValue('resume-summary-ru', 'Обновленная сводка');

    fixture.componentInstance.saveResume();

    expect(service.updateResume).toHaveBeenCalledWith(
      7,
      expect.objectContaining({
        title: 'Target backend resume',
        content: expect.objectContaining({
          summary: {
            textRu: 'Обновленная сводка',
            textEn: 'Strong backend experience.',
          },
          education: [],
          languages: [],
          certifications: [],
          additionalSections: [],
        }),
      }) satisfies ResumePayload,
    );
    expect(notifications.success).toHaveBeenCalledWith('Резюме сохранено.');
  });

  it('renders preview from unsaved form state', () => {
    fixture.componentInstance.setActiveTab('summary');
    fixture.detectChanges();
    setInputValue('resume-summary-ru', 'Несохраненная сводка');

    fixture.componentInstance.showPreview();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="resume-preview"]')).not.toBe(null);
    expect(fixture.nativeElement.textContent).toContain('Несохраненная сводка');
  });

  it('switches preview language', () => {
    fixture.componentInstance.showPreview();
    i18n.switchLanguage('en').subscribe();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Backend engineer');
    expect(fixture.nativeElement.textContent).toContain('Strong backend experience.');
    expect(fixture.nativeElement.textContent).not.toContain('Backend инженер');
  });

  it('does not render a separate preview language switcher', () => {
    fixture.componentInstance.showPreview();
    fixture.detectChanges();

    const previewButtons = Array.from(
      fixture.nativeElement.querySelectorAll('[data-testid="resume-preview"] button'),
    ) as HTMLButtonElement[];

    expect(previewButtons).toEqual([]);
  });

  it('renders edit and preview mode controls as grey buttons', () => {
    const buttons = Array.from(
      fixture.nativeElement.querySelectorAll('button'),
    ) as HTMLButtonElement[];
    const editButton = buttons.find((button) => button.textContent?.includes('Редактирование'));
    const previewButton = buttons.find((button) => button.textContent?.includes('Предпросмотр'));

    expect(editButton?.classList).toContain('btn-secondary');
    expect(editButton?.classList).not.toContain('btn-primary');
    expect(previewButton?.classList).toContain('btn-outline-secondary');
    expect(previewButton?.classList).not.toContain('btn-outline-primary');
  });

  it('renders the back action with a left arrow icon', () => {
    const backButton = Array.from(fixture.nativeElement.querySelectorAll('button')).find((button) =>
      button.textContent?.includes('Назад'),
    ) as HTMLButtonElement | undefined;

    expect(backButton?.querySelector('svg')).not.toBeNull();
  });

  it('uses green outline add actions in repeatable resume sections', () => {
    fixture.componentInstance.setActiveTab('skills');
    fixture.detectChanges();

    const addButton = Array.from(fixture.nativeElement.querySelectorAll('button')).find((button) =>
      button.textContent?.includes('Добавить'),
    ) as HTMLButtonElement | undefined;

    expect(addButton?.classList).toContain('btn-outline-success');
    expect(addButton?.classList).not.toContain('btn-outline-primary');
  });

  it('deletes the resume and returns to the list', () => {
    jest.spyOn(window, 'confirm').mockReturnValue(true);

    fixture.componentInstance.deleteResume();

    expect(service.deleteResume).toHaveBeenCalledWith(7);
    expect(router.navigateByUrl).toHaveBeenCalledWith('/admin-panel/workspace/resumes');
  });

  it('updates payload when a repeatable skill section is added and removed', () => {
    fixture.componentInstance.setActiveTab('skills');
    fixture.componentInstance.addSkillGroup();
    fixture.detectChanges();
    setInputValue('resume-skill-1-category-ru', 'Платформа');
    setInputValue('resume-skill-1-category-en', 'Platform');
    setInputValue('resume-skill-1-items', 'Kubernetes\nPostgreSQL');

    fixture.componentInstance.removeSkillGroup(0);
    fixture.componentInstance.saveResume();

    expect(service.updateResume).toHaveBeenCalledWith(
      7,
      expect.objectContaining({
        content: expect.objectContaining({
          skills: [
            {
              categoryRu: 'Платформа',
              categoryEn: 'Platform',
              items: ['Kubernetes', 'PostgreSQL'],
            },
          ],
        }),
      }),
    );
  });

  it('updates payload when an experience project is edited', () => {
    fixture.componentInstance.setActiveTab('experience');
    fixture.detectChanges();

    expect(elementValueById('resume-experience-0-project-0-name-ru')).toBe('Портфолио');

    setElementValueById('resume-experience-0-project-0-name-ru', 'Платформа');
    setElementValueById('resume-experience-0-project-0-technologies', 'Litestar\nAngular');

    fixture.componentInstance.saveResume();

    expect(service.updateResume).toHaveBeenLastCalledWith(
      7,
      expect.objectContaining({
        content: expect.objectContaining({
          experience: [
            expect.objectContaining({
              projects: [
                expect.objectContaining({
                  nameRu: 'Платформа',
                  nameEn: 'Portfolio',
                  technologies: ['Litestar', 'Angular'],
                }),
              ],
            }),
          ],
        }),
      }),
    );
  });

  it('renders experience projects in the preview', () => {
    fixture.componentInstance.showPreview();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Портфолио');
    expect(fixture.nativeElement.textContent).toContain('Сайт и база знаний');
  });

  it('uses localized date pickers and saves resume dates as ISO values', () => {
    fixture.componentInstance.setActiveTab('experience');
    fixture.detectChanges();

    expect(
      fixture.nativeElement.querySelectorAll('[data-testid="date-picker-toggle"]').length,
    ).toBe(2);

    setElementValueById('resume-experience-0-start-date', '31/01/2024');
    setElementValueById('resume-experience-0-end-date', '01/02/2024');

    fixture.componentInstance.saveResume();

    expect(service.updateResume).toHaveBeenLastCalledWith(
      7,
      expect.objectContaining({
        content: expect.objectContaining({
          experience: [
            expect.objectContaining({
              startDate: '2024-01-31',
              endDate: '2024-02-01',
            }),
          ],
        }),
      }),
    );
  });

  it('saves blank resume text as empty strings, dates as null, and current status as enum', () => {
    fixture.componentInstance.setActiveTab('summary');
    fixture.detectChanges();
    setInputValue('resume-summary-ru', '   ');

    fixture.componentInstance.setActiveTab('experience');
    fixture.detectChanges();
    setElementValueById('resume-experience-0-start-date', '');
    setElementValueById('resume-experience-current-0', 'notSet');

    fixture.componentInstance.saveResume();

    expect(service.updateResume).toHaveBeenLastCalledWith(
      7,
      expect.objectContaining({
        content: expect.objectContaining({
          summary: expect.objectContaining({
            textRu: '',
          }),
          experience: [
            expect.objectContaining({
              startDate: null,
              currentStatus: 'notSet',
            }),
          ],
        }),
      }),
    );
  });

  it('shows an API error notification on save failure', () => {
    service.updateResume.mockReturnValue(throwError(() => apiError()));

    fixture.componentInstance.saveResume();

    expect(notifications.error).toHaveBeenCalledWith('Не удалось сохранить резюме.');
  });

  function inputValue(testId: string): string {
    const input = fixture.nativeElement.querySelector(`[data-testid="${testId}"]`) as
      | HTMLInputElement
      | HTMLTextAreaElement;
    return input.value;
  }

  function setInputValue(testId: string, value: string): void {
    const input = fixture.nativeElement.querySelector(`[data-testid="${testId}"]`) as
      | HTMLInputElement
      | HTMLTextAreaElement;
    input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    fixture.detectChanges();
  }

  function setElementValueById(elementId: string, value: string): void {
    const input = fixture.nativeElement.querySelector(`#${elementId}`) as
      | HTMLInputElement
      | HTMLTextAreaElement
      | HTMLSelectElement;
    input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    fixture.detectChanges();
  }

  function elementValueById(elementId: string): string {
    const input = fixture.nativeElement.querySelector(`#${elementId}`) as
      | HTMLInputElement
      | HTMLTextAreaElement;
    return input.value;
  }
});

function resume(overrides: Partial<Resume> = {}): Resume {
  return {
    id: 7,
    title: 'Backend resume',
    createdAt: '2026-01-01T03:04:05+00:00',
    updatedAt: '2026-01-02T03:04:05+00:00',
    content: {
      profile: {
        fullName: 'Candidate Name',
        roleRu: 'Backend инженер',
        roleEn: 'Backend engineer',
        locationRu: 'Москва',
        locationEn: 'Moscow',
        email: 'candidate@example.com',
        phone: '',
        websiteUrl: '',
        linkedinUrl: '',
        githubUrl: '',
        telegram: '',
      },
      summary: {
        textRu: 'Сильный backend опыт.',
        textEn: 'Strong backend experience.',
      },
      skills: [
        {
          categoryRu: 'Backend',
          categoryEn: 'Backend',
          items: ['Python', 'SQLAlchemy'],
        },
      ],
      experience: [
        {
          companyRu: 'Компания',
          companyEn: 'Company',
          positionRu: 'Инженер',
          positionEn: 'Engineer',
          locationRu: 'Москва',
          locationEn: 'Moscow',
          startDate: '2024-01-01',
          endDate: null,
          currentStatus: 'current',
          summaryRu: 'Разрабатывал API.',
          summaryEn: 'Built APIs.',
          highlightsRu: ['Ускорил сервис'],
          highlightsEn: ['Improved service speed'],
          technologies: ['Python'],
          projects: [
            {
              nameRu: 'Портфолио',
              nameEn: 'Portfolio',
              roleRu: 'Автор',
              roleEn: 'Creator',
              descriptionRu: 'Сайт и база знаний',
              descriptionEn: 'Site and knowledge base',
              highlightsRu: ['Гибридный SSR/CSR'],
              highlightsEn: ['Hybrid SSR/CSR'],
              technologies: ['Litestar'],
              url: 'https://example.com',
            },
          ],
        },
      ],
      education: [],
      languages: [],
      certifications: [],
      additionalSections: [],
    },
    ...overrides,
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
