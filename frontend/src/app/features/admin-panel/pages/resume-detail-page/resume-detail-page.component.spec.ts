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
    exportResume: jest.Mock;
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
      exportResume: jest
        .fn()
        .mockReturnValue(of(new Blob(['resume'], { type: 'application/pdf' }))),
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
    Object.defineProperty(window.URL, 'createObjectURL', {
      configurable: true,
      value: jest.fn().mockReturnValue('blob:resume-export'),
    });
    Object.defineProperty(window.URL, 'revokeObjectURL', {
      configurable: true,
      value: jest.fn(),
    });
    jest.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    fixture = TestBed.createComponent(AdminResumeDetailPageComponent);
    fixture.detectChanges();
  });

  it('loads detail into the edit form', () => {
    expect(service.getResume).toHaveBeenCalledWith(7);
    expect(inputValue('resume-title')).toBe('Backend resume');
    expect(inputValue('resume-language')).toBe('ru');
    expect(inputValue('resume-profile-full-name')).toBe('Candidate Name');
    fixture.componentInstance.setActiveTab('summary');
    fixture.detectChanges();
    expect(inputValue('resume-summary')).toBe('Сильный backend опыт.');
    expect(fixture.nativeElement.textContent).toContain('Профиль');
    expect(fixture.nativeElement.textContent).toContain('Навыки');
  });

  it('edits and saves an explicit update payload', () => {
    setInputValue('resume-title', 'Target backend resume');
    setInputValue('resume-language', 'en');
    fixture.componentInstance.setActiveTab('summary');
    fixture.detectChanges();
    setInputValue('resume-summary', 'Updated summary');

    fixture.componentInstance.saveResume();

    expect(service.updateResume).toHaveBeenCalledWith(
      7,
      expect.objectContaining({
        title: 'Target backend resume',
        language: 'en',
        content: expect.objectContaining({
          summary: {
            text: 'Updated summary',
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
    setInputValue('resume-summary', 'Несохраненная сводка');

    fixture.componentInstance.showPreview();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="resume-preview"]')).not.toBe(null);
    expect(fixture.nativeElement.textContent).toContain('Несохраненная сводка');
  });

  it('keeps preview language tied to the resume language, not UI language', () => {
    fixture.componentInstance.showPreview();
    i18n.switchLanguage('en').subscribe();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Backend инженер');
    expect(fixture.nativeElement.textContent).toContain('Сильный backend опыт.');
    expect(fixture.nativeElement.textContent).toContain('Саммари');
    expect(fixture.nativeElement.textContent).not.toContain('Strong backend experience.');
    expect(fixture.nativeElement.textContent).not.toContain('Summary');
  });

  it('renders the back action with a left arrow icon', () => {
    const backButton = Array.from(fixture.nativeElement.querySelectorAll('button')).find((button) =>
      button.textContent?.includes('Назад'),
    ) as HTMLButtonElement | undefined;

    expect(backButton?.querySelector('svg')).not.toBeNull();
  });

  it('renders save, export, and delete as accessible icon buttons', () => {
    const saveButton = buttonByLabel('Сохранить');
    const exportButton = buttonByLabel('Экспорт');
    const deleteButton = buttonByLabel('Удалить');

    expect(saveButton.querySelector('svg')).not.toBeNull();
    expect(exportButton.querySelector('svg')).not.toBeNull();
    expect(deleteButton.querySelector('svg')).not.toBeNull();
    expect(textNodeContent(saveButton)).toBe('');
    expect(textNodeContent(exportButton)).toBe('');
    expect(textNodeContent(deleteButton)).toBe('');
  });

  it('opens and closes the export modal', () => {
    buttonByLabel('Экспорт').click();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[role="dialog"]')).not.toBeNull();
    expect(fixture.nativeElement.textContent).toContain('Формат');
    expect(fixture.nativeElement.textContent).toContain('Выберите формат');
    expect(elementByTestId<HTMLSelectElement>('resume-export-format').value).toBe('');
    expect(elementByTestId<HTMLButtonElement>('resume-export-submit').disabled).toBe(true);
    expect(fixture.nativeElement.querySelector('.resume-export-modal .btn-warning')).toBeNull();

    buttonByLabel('Закрыть').click();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[role="dialog"]')).toBeNull();
  });

  it('exports unsaved form edits in the selected format', () => {
    fixture.componentInstance.setActiveTab('summary');
    fixture.detectChanges();
    setInputValue('resume-summary', 'Unsaved export summary');

    buttonByLabel('Экспорт').click();
    fixture.detectChanges();
    setInputValue('resume-export-format', 'docx');
    elementByTestId<HTMLButtonElement>('resume-export-submit').click();
    fixture.detectChanges();

    expect(service.exportResume).toHaveBeenCalledWith(
      7,
      'docx',
      expect.objectContaining({
        content: expect.objectContaining({
          summary: {
            text: 'Unsaved export summary',
          },
        }),
      }),
    );
    expect(window.URL.createObjectURL).toHaveBeenCalled();
    expect(notifications.success).toHaveBeenCalledWith('Резюме экспортировано.');
  });

  it('blocks export when the current form is invalid', () => {
    setInputValue('resume-title', '');

    buttonByLabel('Экспорт').click();
    fixture.detectChanges();
    setInputValue('resume-export-format', 'pdf');
    elementByTestId<HTMLButtonElement>('resume-export-submit').click();
    fixture.detectChanges();

    expect(service.exportResume).not.toHaveBeenCalled();
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
    setInputValue('resume-skill-1-category', 'Платформа');
    setInputValue('resume-skill-1-items', 'Kubernetes\nPostgreSQL');

    fixture.componentInstance.removeSkillGroup(0);
    fixture.componentInstance.saveResume();

    expect(service.updateResume).toHaveBeenCalledWith(
      7,
      expect.objectContaining({
        content: expect.objectContaining({
          skills: [
            {
              category: 'Платформа',
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

    expect(elementValueById('resume-experience-0-project-0-name')).toBe('Портфолио');

    setElementValueById('resume-experience-0-project-0-name', 'Платформа');
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
                  name: 'Платформа',
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
    setInputValue('resume-summary', '   ');

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
            text: '',
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
      | HTMLTextAreaElement
      | HTMLSelectElement;
    return input.value;
  }

  function setInputValue(testId: string, value: string): void {
    const input = fixture.nativeElement.querySelector(`[data-testid="${testId}"]`) as
      | HTMLInputElement
      | HTMLTextAreaElement
      | HTMLSelectElement;
    input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
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

  function buttonByLabel(label: string): HTMLButtonElement {
    const button = fixture.nativeElement.querySelector(
      `button[aria-label="${label}"]`,
    ) as HTMLButtonElement | null;
    expect(button).not.toBeNull();
    return button as HTMLButtonElement;
  }

  function elementByTestId<TElement extends HTMLElement>(testId: string): TElement {
    const element = fixture.nativeElement.querySelector(
      `[data-testid="${testId}"]`,
    ) as TElement | null;
    expect(element).not.toBeNull();
    return element as TElement;
  }

  function textNodeContent(button: HTMLButtonElement): string {
    return Array.from(button.childNodes)
      .filter((node) => node.nodeType === Node.TEXT_NODE)
      .map((node) => node.textContent?.trim() ?? '')
      .join('');
  }
});

function resume(overrides: Partial<Resume> = {}): Resume {
  return {
    id: 7,
    title: 'Backend resume',
    language: 'ru',
    createdAt: '2026-01-01T03:04:05+00:00',
    updatedAt: '2026-01-02T03:04:05+00:00',
    content: {
      profile: {
        fullName: 'Candidate Name',
        role: 'Backend инженер',
        location: 'Москва',
        email: 'candidate@example.com',
        phone: '',
        websiteUrl: '',
        linkedinUrl: '',
        githubUrl: '',
        telegram: '',
      },
      summary: {
        text: 'Сильный backend опыт.',
      },
      skills: [
        {
          category: 'Backend',
          items: ['Python', 'SQLAlchemy'],
        },
      ],
      experience: [
        {
          company: 'Компания',
          position: 'Инженер',
          location: 'Москва',
          startDate: '2024-01-01',
          endDate: null,
          currentStatus: 'current',
          summary: 'Разрабатывал API.',
          highlights: ['Ускорил сервис'],
          technologies: ['Python'],
          projects: [
            {
              name: 'Портфолио',
              role: 'Автор',
              description: 'Сайт и база знаний',
              highlights: ['Гибридный SSR/CSR'],
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
