import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthModalService } from '../../../../core/auth/auth-modal.service';
import { AuthService } from '../../../../core/auth/auth.service';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { LanguageCode } from '../../../../core/i18n/i18n.model';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { ThemeService } from '../../../../core/layout/theme.service';
import { localizedPublicHomePath } from '../../../../core/routing/public-home';

interface LanguageOption {
  code: LanguageCode;
  label: string;
  shortLabel: string;
  selected: boolean;
}

@Component({
  selector: 'app-admin-panel-header',
  standalone: true,
  imports: [RouterLink, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './admin-panel-header.component.html',
  styleUrl: './admin-panel-header.component.scss',
})
export class AdminPanelHeaderComponent {
  private readonly authModal = inject(AuthModalService);
  private readonly authService = inject(AuthService);
  private readonly i18n = inject(I18nService);
  private readonly themeService = inject(ThemeService);

  readonly homeLink = computed(() => localizedPublicHomePath(this.currentLanguage()));
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

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  switchLanguage(language: LanguageCode): void {
    this.i18n.switchLanguage(language).subscribe();
  }

  openLogin(): void {
    this.authModal.openLogin();
  }

  logout(): void {
    this.authService.logout().subscribe({
      error: () => {
        this.authService.clearLocalSession();
      },
    });
  }

  private currentLanguage(): LanguageCode {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }
}
