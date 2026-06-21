import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { Router, provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { SiteHeaderComponent, rewriteLanguagePrefixedUrl } from './site-header.component';
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
  let router: Router;
  let mockThemeService: {
    theme: ReturnType<typeof signal<ThemeName>>;
    toggleTheme: jest.Mock;
    setTheme: jest.Mock;
  };
  let mockAuthService: {
    currentUser: ReturnType<typeof signal<AccountInfo | null>>;
    isLoggedIn: () => boolean;
    canManageContent: () => boolean;
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
      canManageContent: () => {
        const role = currentUserSignal()?.role;
        return role === 'admin' || role === 'moderator';
      },
      logout: jest.fn().mockReturnValue({ subscribe: jest.fn() }),
    };
    mockAuthModalService = {
      openLogin: jest.fn(),
    };
    mockI18nService = {
      language: languageSignal,
      languages: languagesSignal,
      switchLanguage: jest.fn().mockReturnValue(of(void 0)),
      translate: jest.fn((key: string, params?: Record<string, string | number>) => {
        const messages: Record<string, string> = {
          'shell.nav.about': 'Обо мне',
          'shell.nav.matrix': 'Матрица компетенций',
          'shell.nav.articles': 'Статьи',
          'shell.nav.adminPanel': 'Админ-панель',
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
    router = TestBed.inject(Router);
  });

  it('renders nav link to the localized about page', () => {
    expect(fixture.componentInstance.aboutLink()).toBe('/ru/about-me');
  });

  it('renders nav link to the localized competency matrix page', () => {
    expect(fixture.componentInstance.matrixLink()).toBe('/ru/competency-matrix');
  });

  it('renders nav link to the localized articles page', () => {
    expect(fixture.componentInstance.articlesLink()).toBe('/ru/articles');
  });

  it('hides admin-panel navigation from guests and regular users', () => {
    expect(el.querySelector('a[aria-label="Админ-панель"]')).toBeNull();

    currentUserSignal.set({ username: 'user', role: 'user' });
    fixture.detectChanges();

    expect(el.querySelector('a[aria-label="Админ-панель"]')).toBeNull();
  });

  it('shows admin-panel navigation to moderators and admins', () => {
    currentUserSignal.set({ username: 'moderator', role: 'moderator' });
    fixture.detectChanges();

    let adminLink = el.querySelector('a[aria-label="Админ-панель"]') as HTMLAnchorElement;
    expect(adminLink).not.toBeNull();
    expect(adminLink.getAttribute('href')).toBe('/admin-panel');

    currentUserSignal.set({ username: 'admin', role: 'admin' });
    fixture.detectChanges();

    adminLink = el.querySelector('a[aria-label="Админ-панель"]') as HTMLAnchorElement;
    expect(adminLink).not.toBeNull();
  });

  it('theme toggle button calls themeService.toggleTheme()', () => {
    const button = findButtonByText(el, 'Dark');
    expect(button).not.toBeNull();
    button.click();
    expect(mockThemeService.toggleTheme).toHaveBeenCalled();
  });

  it('toggle button text reflects current theme label', () => {
    const button = findButtonByText(el, 'Dark');
    expect(button).not.toBeNull();
    expect(button.getAttribute('aria-label')).toBeNull();
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

  it('shows username and logout button when logged in', () => {
    currentUserSignal.set({ username: 'admin', role: 'admin' });
    fixture.detectChanges();

    const logoutBtn = el.querySelector('button[aria-label="Выйти"]') as HTMLButtonElement;
    expect(logoutBtn).not.toBeNull();

    const usernameEl = el.querySelector('[aria-label="Вы вошли как admin"]');
    expect(usernameEl).not.toBeNull();
    expect(usernameEl?.textContent?.trim()).toBe('admin');
  });

  it('calls authService.logout() when logout button is clicked', () => {
    currentUserSignal.set({ username: 'admin', role: 'admin' });
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

  it('switches language and rewrites the current localized URL', () => {
    jest.spyOn(router, 'url', 'get').mockReturnValue('/ru/articles/typed-articles?tag=angular');
    const navigateByUrlSpy = jest.spyOn(router, 'navigateByUrl').mockResolvedValue(true);
    const englishButton = Array.from(el.querySelectorAll('button')).find(
      (button) => button.textContent?.trim() === 'EN',
    ) as HTMLButtonElement;

    englishButton.click();

    expect(mockI18nService.switchLanguage).toHaveBeenCalledWith('en');
    expect(navigateByUrlSpy).toHaveBeenCalledWith('/en/articles/typed-articles?tag=angular');
  });

  it('rewrites the site-build case-study URL between localized public routes', () => {
    expect(rewriteLanguagePrefixedUrl('/ru/how-this-site-is-built#quality', 'en')).toBe(
      '/en/how-this-site-is-built#quality',
    );
    expect(rewriteLanguagePrefixedUrl('/how-this-site-is-built', 'ru')).toBe(
      '/ru/how-this-site-is-built',
    );
  });
});

function findButtonByText(root: ParentNode, text: string): HTMLButtonElement {
  const button = Array.from(root.querySelectorAll<HTMLButtonElement>('button')).find(
    (item) => item.textContent?.trim() === text,
  );
  if (button === undefined) {
    throw new Error(`Missing ${text} button.`);
  }
  return button;
}
