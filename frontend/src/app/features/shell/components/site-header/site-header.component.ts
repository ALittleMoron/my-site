import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { ThemeService } from '../../../../core/layout/theme.service';
import { AuthService } from '../../../../core/auth/auth.service';
import { AuthModalService } from '../../../../core/auth/auth-modal.service';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { LanguageCode } from '../../../../core/i18n/i18n.model';

interface LanguageOption {
  code: LanguageCode;
  label: string;
  shortLabel: string;
  selected: boolean;
}

@Component({
  selector: 'app-site-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './site-header.component.html',
})
export class SiteHeaderComponent {
  private readonly themeService = inject(ThemeService);
  private readonly authService = inject(AuthService);
  private readonly authModal = inject(AuthModalService);
  private readonly i18n = inject(I18nService);

  readonly isNavOpen = signal(false);
  readonly toggleLabel = computed(() =>
    this.i18n.translate(
      this.themeService.theme() === 'light' ? 'shell.theme.dark' : 'shell.theme.light',
    ),
  );
  readonly isLoggedIn = computed(() => this.authService.isLoggedIn());
  readonly username = computed(() => this.authService.currentUser()?.username ?? null);
  readonly languageOptions = computed<LanguageOption[]>(() => {
    const currentLanguage = this.i18n.language();
    return this.i18n.languages().map((language) => ({
      code: language.code,
      label: language.label,
      shortLabel: language.code.toUpperCase(),
      selected: language.code === currentLanguage,
    }));
  });

  toggleNav(): void {
    this.isNavOpen.update((v) => !v);
  }

  closeNav(): void {
    this.isNavOpen.set(false);
  }

  toggle(): void {
    this.themeService.toggleTheme();
  }

  openLogin(): void {
    this.authModal.openLogin();
  }

  logout(): void {
    this.authService.logout().subscribe({
      error: () => {
        // Force local logout even if server endpoint fails
        this.authService.clearLocalSession();
      },
    });
  }

  switchLanguage(language: LanguageCode): void {
    this.i18n.switchLanguage(language).subscribe();
  }
}
