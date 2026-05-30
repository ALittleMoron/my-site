import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ConsentService } from '../../../../core/privacy/consent.service';

@Component({
  selector: 'app-cookie-consent-banner',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (!consent.cookieConsentAccepted()) {
      <section
        class="cookie-consent-banner position-fixed bottom-0 start-0 end-0 p-3"
        data-testid="cookie-consent"
        aria-live="polite"
      >
        <div class="container d-flex flex-column flex-md-row gap-3 align-items-md-center">
          <p class="m-0 flex-grow-1">
            Сайт использует локальное хранилище для базовой работы интерфейса, сохранения настроек и
            анонимных реакций. Просмотры считаются агрегированно, без аналитических cookies.
          </p>
          <button type="button" class="btn button-active" (click)="consent.acceptCookieConsent()">
            Хорошо
          </button>
        </div>
      </section>
    }
  `,
})
export class CookieConsentBannerComponent {
  readonly consent = inject(ConsentService);
}
