import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app.component';
import { AuthService } from './core/auth/auth.service';
import { AuthModalService } from './core/auth/auth-modal.service';
import { ThemeService } from './core/layout/theme.service';

describe('AppComponent', () => {
  let fixture: ComponentFixture<AppComponent>;
  let isLoginOpen: ReturnType<typeof signal<boolean>>;

  beforeEach(async () => {
    isLoginOpen = signal(false);

    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [
        provideRouter([]),
        {
          provide: AuthModalService,
          useValue: {
            isLoginOpen,
            openLogin: jest.fn(),
            closeLogin: jest.fn(() => isLoginOpen.set(false)),
          },
        },
        {
          provide: AuthService,
          useValue: {
            currentUser: signal(null),
            isLoggedIn: () => false,
            logout: jest.fn(),
            login: jest.fn(),
          },
        },
        {
          provide: ThemeService,
          useValue: {
            theme: signal('light'),
            toggleTheme: jest.fn(),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
  });

  it('applies the legacy gradient body class to the page shell', () => {
    const shell = fixture.nativeElement.querySelector('.app-shell') as HTMLElement;
    expect(shell).not.toBeNull();
    expect(shell.classList).toContain('gradient-body');
  });

  it('renders the login component as a modal when requested', () => {
    isLoginOpen.set(true);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-login-page')).not.toBeNull();
  });
});
