import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { provideRouter } from '@angular/router';
import { SiteHeaderComponent } from './site-header.component';
import { ThemeService } from '../../../../core/layout/theme.service';
import { ThemeName } from '../../../../core/layout/theme.service';
import { AuthService, AccountInfo } from '../../../../core/auth/auth.service';
import { AuthModalService } from '../../../../core/auth/auth-modal.service';

describe('SiteHeaderComponent', () => {
  let fixture: ComponentFixture<SiteHeaderComponent>;
  let el: HTMLElement;
  let themeSignal: ReturnType<typeof signal<ThemeName>>;
  let currentUserSignal: ReturnType<typeof signal<AccountInfo | null>>;
  let mockThemeService: {
    theme: ReturnType<typeof signal<ThemeName>>;
    toggleTheme: jest.Mock;
    setTheme: jest.Mock;
  };
  let mockAuthService: {
    currentUser: ReturnType<typeof signal<AccountInfo | null>>;
    isLoggedIn: () => boolean;
    logout: jest.Mock;
  };
  let mockAuthModalService: { openLogin: jest.Mock };

  beforeEach(async () => {
    themeSignal = signal<ThemeName>('light');
    currentUserSignal = signal<AccountInfo | null>(null);

    mockThemeService = {
      theme: themeSignal,
      toggleTheme: jest.fn(),
      setTheme: jest.fn(),
    };

    mockAuthService = {
      currentUser: currentUserSignal,
      isLoggedIn: () => currentUserSignal() !== null,
      logout: jest.fn().mockReturnValue({ subscribe: jest.fn() }),
    };
    mockAuthModalService = {
      openLogin: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [SiteHeaderComponent],
      providers: [
        provideRouter([]),
        { provide: ThemeService, useValue: mockThemeService },
        { provide: AuthService, useValue: mockAuthService },
        { provide: AuthModalService, useValue: mockAuthModalService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(SiteHeaderComponent);
    fixture.detectChanges();
    el = fixture.nativeElement as HTMLElement;
  });

  it('renders nav link to /about-me', () => {
    const links = el.querySelectorAll('a[routerLink]');
    const hrefs = Array.from(links).map(
      (a) => a.getAttribute('routerLink') ?? a.getAttribute('href'),
    );
    expect(hrefs).toContain('/about-me');
  });

  it('renders nav link to /competency-matrix', () => {
    const links = el.querySelectorAll('a[routerLink]');
    const hrefs = Array.from(links).map(
      (a) => a.getAttribute('routerLink') ?? a.getAttribute('href'),
    );
    expect(hrefs).toContain('/competency-matrix');
  });

  it('renders nav link to /notes', () => {
    const links = el.querySelectorAll('a[routerLink]');
    const hrefs = Array.from(links).map(
      (a) => a.getAttribute('routerLink') ?? a.getAttribute('href'),
    );
    expect(hrefs).toContain('/notes');
  });

  it('theme toggle button calls themeService.toggleTheme()', () => {
    const button = el.querySelector('button[aria-label="Toggle theme"]') as HTMLButtonElement;
    expect(button).not.toBeNull();
    button.click();
    expect(mockThemeService.toggleTheme).toHaveBeenCalled();
  });

  it('toggle button text reflects current theme label', () => {
    const button = el.querySelector('button[aria-label="Toggle theme"]') as HTMLButtonElement;
    expect(button).not.toBeNull();
    expect(button.textContent?.trim()).toBe('Dark');

    themeSignal.set('dark');
    fixture.detectChanges();
    expect(button.textContent?.trim()).toBe('Light');
  });

  it('shows login modal button when user is not logged in', () => {
    const loginButton = el.querySelector('button[aria-label="Войти"]') as HTMLButtonElement;
    expect(loginButton).not.toBeNull();
    expect(loginButton.textContent?.trim()).toBe('Войти');
    expect(el.querySelector('a[routerLink="/login"]')).toBeNull();
  });

  it('opens login modal when login button is clicked', () => {
    const loginButton = el.querySelector('button[aria-label="Войти"]') as HTMLButtonElement;
    loginButton.click();
    expect(mockAuthModalService.openLogin).toHaveBeenCalled();
  });

  it('uses the carried-over navbar and button utility styles', () => {
    const nav = el.querySelector('nav');
    expect(nav?.classList).toContain('nav-blur');

    const themeButton = el.querySelector('button[aria-label="Toggle theme"]') as HTMLButtonElement;
    expect(themeButton.classList).toContain('button-inactive');
  });

  it('shows username and logout button when logged in', () => {
    currentUserSignal.set({ username: 'admin', role: 'Admin' });
    fixture.detectChanges();

    const logoutBtn = el.querySelector('button[aria-label="Выйти"]') as HTMLButtonElement;
    expect(logoutBtn).not.toBeNull();

    const usernameEl = el.querySelector('[aria-label="Logged in as admin"]');
    expect(usernameEl).not.toBeNull();
    expect(usernameEl?.textContent?.trim()).toBe('admin');
  });

  it('calls authService.logout() when logout button is clicked', () => {
    currentUserSignal.set({ username: 'admin', role: 'Admin' });
    fixture.detectChanges();

    const logoutBtn = el.querySelector('button[aria-label="Выйти"]') as HTMLButtonElement;
    logoutBtn.click();
    expect(mockAuthService.logout).toHaveBeenCalled();
  });
});
