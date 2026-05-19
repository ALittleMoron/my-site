import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AuthModalService } from './core/auth/auth-modal.service';
import { LoginPageComponent } from './features/auth/pages/login-page/login-page.component';
import { SiteFooterComponent } from './features/shell/components/site-footer/site-footer.component';
import { SiteHeaderComponent } from './features/shell/components/site-header/site-header.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, SiteHeaderComponent, SiteFooterComponent, LoginPageComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="app-shell gradient-body d-flex flex-column min-vh-100">
      <app-site-header />
      <router-outlet />
      <app-site-footer class="mt-auto" />
      @if (authModal.isLoginOpen()) {
        <app-login-page />
      }
    </div>
  `,
})
export class AppComponent {
  readonly authModal = inject(AuthModalService);
}
