import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AuthModalService } from './core/auth/auth-modal.service';
import { LoginPageComponent } from './features/auth/pages/login-page/login-page.component';
import { CookieConsentBannerComponent } from './features/shell/components/cookie-consent-banner/cookie-consent-banner.component';
import { NotificationAreaComponent } from './features/shell/components/notification-area/notification-area.component';
import { SiteFooterComponent } from './features/shell/components/site-footer/site-footer.component';
import { SiteHeaderComponent } from './features/shell/components/site-header/site-header.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    SiteHeaderComponent,
    SiteFooterComponent,
    LoginPageComponent,
    NotificationAreaComponent,
    CookieConsentBannerComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="app-shell gradient-body d-flex flex-column min-vh-100">
      <app-site-header />
      <app-notification-area />
      <router-outlet />
      <app-site-footer class="mt-auto" />
      <app-cookie-consent-banner />
      @if (authModal.isLoginOpen()) {
        <app-login-page />
      }
    </div>
  `,
})
export class AppComponent {
  readonly authModal = inject(AuthModalService);
}
