import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WritableSignal, signal } from '@angular/core';
import { provideRouter } from '@angular/router';
import { AccountInfo, AuthService } from '../../../../core/auth/auth.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { AdminPanelPageComponent } from './admin-panel-page.component';

describe('AdminPanelPageComponent', () => {
  let fixture: ComponentFixture<AdminPanelPageComponent>;
  let currentUser: WritableSignal<AccountInfo | null>;
  let isAdmin: WritableSignal<boolean>;
  let canManageContent: WritableSignal<boolean>;
  let canManageTeam: WritableSignal<boolean>;
  let isLoggedIn: WritableSignal<boolean>;

  beforeEach(async () => {
    currentUser = signal({ username: 'admin', role: 'admin' });
    isAdmin = signal(true);
    canManageContent = signal(true);
    canManageTeam = signal(true);
    isLoggedIn = signal(true);
    await TestBed.configureTestingModule({
      imports: [AdminPanelPageComponent],
      providers: [
        provideRouter([]),
        provideI18nTesting(),
        {
          provide: AuthService,
          useValue: {
            currentUser,
            isAdmin,
            canManageContent,
            canManageTeam,
            isLoggedIn,
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminPanelPageComponent);
    fixture.detectChanges();
  });

  it('renders the admin header, workspace, and matrix question queue section for admins', () => {
    expect(fixture.nativeElement.querySelector('app-admin-panel-header')).not.toBeNull();
    expect(
      fixture.nativeElement.querySelector('[data-testid="admin-panel-side-panel"]'),
    ).not.toBeNull();
    expect(fixture.nativeElement.textContent).toContain('Разделы');
    expect(fixture.nativeElement.textContent).toContain('Рабочая область');
    expect(fixture.nativeElement.textContent).toContain('Команда');
    expect(fixture.nativeElement.textContent).toContain('Резюме');
    expect(fixture.nativeElement.textContent).toContain('Вопросы матрицы');
    expect(fixture.nativeElement.textContent).toContain('Структура матрицы');
    expect(fixture.nativeElement.textContent).toContain('Очередь вопросов матрицы');
  });

  it('places workspace navigation first in the side panel', () => {
    const sections = Array.from(
      fixture.nativeElement.querySelectorAll('[data-testid="admin-panel-tree-section"]'),
    ) as HTMLButtonElement[];

    expect(sections.map((section) => section.textContent?.trim().replace(/^[-+]\s*/, ''))).toEqual([
      'Рабочая область2',
      'Статьи1',
      'Матрица3',
    ]);
  });

  it('hides team workspace navigation from non-team content managers', () => {
    isAdmin.set(false);
    canManageTeam.set(false);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).not.toContain('Рабочая область');
    expect(fixture.nativeElement.textContent).not.toContain('Команда');
    expect(fixture.nativeElement.textContent).not.toContain('Резюме');
    expect(fixture.nativeElement.textContent).toContain('Вопросы матрицы');
  });

  it('shows workspace navigation for owners without exact admin access', () => {
    currentUser.set({ username: 'owner', role: 'owner' });
    isAdmin.set(false);
    canManageTeam.set(true);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Рабочая область');
    expect(fixture.nativeElement.textContent).toContain('Команда');
    expect(fixture.nativeElement.textContent).toContain('Резюме');
  });

  it('opens and closes the mobile drawer without removing the desktop side panel', () => {
    const toggle = fixture.nativeElement.querySelector(
      '[data-testid="admin-panel-side-panel-toggle"]',
    ) as HTMLButtonElement;
    const panel = fixture.nativeElement.querySelector(
      '[data-testid="admin-panel-side-panel"]',
    ) as HTMLElement;

    expect(panel.classList).toContain('admin-panel-side-panel-open');

    toggle.click();
    fixture.detectChanges();

    expect(panel.classList).toContain('admin-panel-side-panel-closed');
    expect(panel.getAttribute('inert')).toBeNull();
    expect(panel.getAttribute('aria-hidden')).toBeNull();
  });
});
