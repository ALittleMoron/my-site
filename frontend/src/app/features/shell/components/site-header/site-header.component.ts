import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { ThemeService } from '../../../../core/layout/theme.service';
import { AuthService } from '../../../../core/auth/auth.service';
import { AuthModalService } from '../../../../core/auth/auth-modal.service';

@Component({
  selector: 'app-site-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './site-header.component.html',
})
export class SiteHeaderComponent {
  private readonly themeService = inject(ThemeService);
  private readonly authService = inject(AuthService);
  private readonly authModal = inject(AuthModalService);

  readonly isNavOpen = signal(false);
  readonly toggleLabel = computed(() =>
    this.themeService.theme() === 'light' ? 'Dark' : 'Light',
  );
  readonly isLoggedIn = computed(() => this.authService.isLoggedIn());
  readonly username = computed(() => this.authService.currentUser()?.username ?? null);

  toggleNav(): void {
    this.isNavOpen.update(v => !v);
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
}
