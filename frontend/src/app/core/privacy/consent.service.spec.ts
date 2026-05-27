import { TestBed } from '@angular/core/testing';
import { ConsentService } from './consent.service';

describe('ConsentService', () => {
  let service: ConsentService;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({});
    service = TestBed.inject(ConsentService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('starts without cookie consent', () => {
    expect(service.cookieConsentAccepted()).toBe(false);
  });

  it('persists accepted cookie consent', () => {
    service.acceptCookieConsent();

    expect(service.cookieConsentAccepted()).toBe(true);
    expect(localStorage.getItem('cookieConsentAccepted')).toBe('true');
  });
});
