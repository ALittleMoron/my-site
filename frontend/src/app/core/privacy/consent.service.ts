import { Injectable, signal } from '@angular/core';

const COOKIE_CONSENT_KEY = 'cookieConsentAccepted';

@Injectable({ providedIn: 'root' })
export class ConsentService {
  readonly cookieConsentAccepted = signal(localStorage.getItem(COOKIE_CONSENT_KEY) === 'true');

  acceptCookieConsent(): void {
    localStorage.setItem(COOKIE_CONSENT_KEY, 'true');
    this.cookieConsentAccepted.set(true);
  }
}
