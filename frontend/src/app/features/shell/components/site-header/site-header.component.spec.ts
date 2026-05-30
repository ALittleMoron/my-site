import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { provideRouter } from '@angular/router';
import { SiteHeaderComponent } from './site-header.component';
import { ThemeService } from '../../../../core/layout/theme.service';
import { ThemeName } from '../../../../core/layout/theme.service';
import { AuthService, AccountInfo } from '../../../../core/auth/auth.service';
import { AuthModalService } from '../../../../core/auth/auth-modal.service';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { I18nLanguage, LanguageCode } from '../../../../core/i18n/i18n.model';

describe('SiteHeaderComponent', () => {
  let fixture: ComponentFixture<SiteHeaderComponent>;
  let el: HTMLElement;
  let themeSignal: ReturnType<typeof signal<ThemeName>>;
  let currentUserSignal: ReturnType<typeof signal<AccountInfo | null>>;
  let languageSignal: ReturnType<typeof signal<LanguageCode | null>>;
  let languagesSignal: ReturnType<typeof signal<I18nLanguage[]>>;
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
  let mockI18nService: {
    language: ReturnType<typeof signal<LanguageCode | null>>;
    languages: ReturnType<typeof signal<I18nLanguage[]>>;
    switchLanguage: jest.Mock;
    translate: jest.Mock;
  };

  beforeEach(async () => {
    themeSignal = signal<ThemeName>('light');
    currentUserSignal = signal<AccountInfo | null>(null);
    languageSignal = signal<LanguageCode | null>('ru');
    languagesSignal = signal<I18nLanguage[]>([
      { code: 'ru', label: 'Русский' },
      { code: 'en', label: 'English' },
    ]);

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
    mockI18nService = {
      language: languageSignal,
      languages: languagesSignal,
      switchLanguage: jest.fn().mockReturnValue({ subscribe: jest.fn() }),
      translate: jest.fn((key: string, params?: Record<string, string | number>) => {
        const messages: Record<string, string> = {
          'shell.nav.about': 'Обо мне',
          'shell.nav.matrix': 'Матрица компетенций',
          'shell.nav.notes': 'Заметки',
          'shell.nav.toggleNavigation': 'Открыть навигацию',
          'shell.theme.dark': 'Dark',
          'shell.theme.light': 'Light',
          'shell.theme.toggle': 'Переключить тему',
          'shell.auth.login': 'Войти',
          'shell.auth.logout': 'Выйти',
          'shell.auth.loggedInAs': 'Вы вошли как {username}',
          'shell.language.label': 'Язык',
        };
        const template = messages[key] ?? key;
        if (!params) return template;
        return Object.entries(params).reduce(
          (text, [name, value]) => text.replaceAll(`{${name}}`, String(value)),
          template,
        );
      }),
    };

    await TestBed.configureTestingModule({
      imports: [SiteHeaderComponent],
      providers: [
        provideRouter([]),
        { provide: ThemeService, useValue: mockThemeService },
        { provide: AuthService, useValue: mockAuthService },
        { provide: AuthModalService, useValue: mockAuthModalService },
        { provide: I18nService, useValue: mockI18nService },
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
    const button = el.querySelector('button[aria-label="Переключить тему"]') as HTMLButtonElement;
    expect(button).not.toBeNull();
    button.click();
    expect(mockThemeService.toggleTheme).toHaveBeenCalled();
  });

  it('toggle button text reflects current theme label', () => {
    const button = el.querySelector('button[aria-label="Переключить тему"]') as HTMLButtonElement;
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

    const themeButton = el.querySelector(
      'button[aria-label="Переключить тему"]',
    ) as HTMLButtonElement;
    expect(themeButton.classList).toContain('button-inactive');
  });

  it('shows username and logout button when logged in', () => {
    currentUserSignal.set({ username: 'admin', role: 'Admin' });
    fixture.detectChanges();

    const logoutBtn = el.querySelector('button[aria-label="Выйти"]') as HTMLButtonElement;
    expect(logoutBtn).not.toBeNull();

    const usernameEl = el.querySelector('[aria-label="Вы вошли как admin"]');
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

  it('renders language switcher with current language selected', () => {
    const switcher = el.querySelector('[aria-label="Язык"]');
    expect(switcher).not.toBeNull();

    const buttons = Array.from(switcher?.querySelectorAll('button') ?? []);
    expect(buttons.map((button) => button.textContent?.trim())).toEqual(['RU', 'EN']);
    expect(buttons[0].getAttribute('aria-pressed')).toBe('true');
    expect(buttons[1].getAttribute('aria-pressed')).toBe('false');
  });

  it('switches language when another language is clicked', () => {
    const englishButton = Array.from(el.querySelectorAll('button')).find(
      (button) => button.textContent?.trim() === 'EN',
    ) as HTMLButtonElement;

    englishButton.click();

    expect(mockI18nService.switchLanguage).toHaveBeenCalledWith('en');
  });
});
