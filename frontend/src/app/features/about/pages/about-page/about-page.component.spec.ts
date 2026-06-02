import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { provideRouter } from '@angular/router';
import { AboutPageComponent } from './about-page.component';
import { ContactService } from '../../services/contact.service';
import { ApiError } from '../../../../core/models/api-error.model';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';

const mockApiError: ApiError = {
  code: 'validation_error',
  type: 'validation_error',
  message: 'Validation failed',
  location: 'body',
  attr: null,
  nested_errors: [
    {
      code: 'max_length',
      type: 'max_length',
      message: 'Ensure this field has no more than 255 characters.',
      location: 'body',
      attr: 'name',
    },
  ],
};

describe('AboutPageComponent', () => {
  let fixture: ComponentFixture<AboutPageComponent>;
  let component: AboutPageComponent;
  let contactService: { createContactRequest: jest.Mock };
  let notificationService: { success: jest.Mock; error: jest.Mock };

  beforeEach(async () => {
    contactService = {
      createContactRequest: jest.fn().mockReturnValue(of(null)),
    };
    notificationService = {
      success: jest.fn(),
      error: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [AboutPageComponent],
      providers: [
        { provide: ContactService, useValue: contactService },
        { provide: NotificationService, useValue: notificationService },
        provideI18nTesting({
          'about.contact.email': 'Эл. почта',
          'about.contact.emailPlaceholder': 'you@example.com',
          'about.contact.telegram': 'Телеграм',
          'about.contact.telegramPlaceholder': '@your_username',
        }),
        provideRouter([]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AboutPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('submit button is disabled when message is empty', () => {
    component.form.setValue({
      name: '',
      email: '',
      telegram: '',
      message: '',
      personalDataConsent: true,
    });
    fixture.detectChanges();
    const button = fixture.nativeElement.querySelector(
      'button[type="submit"]',
    ) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
  });

  it('renders localized contact method labels and placeholders', () => {
    const emailInput = fixture.nativeElement.querySelector(
      '#contact-me-email-field',
    ) as HTMLInputElement;
    const telegramInput = fixture.nativeElement.querySelector(
      '#contact-me-telegram-field',
    ) as HTMLInputElement;

    expect(fixture.nativeElement.textContent).toContain('Эл. почта');
    expect(emailInput.placeholder).toBe('you@example.com');
    expect(fixture.nativeElement.textContent).toContain('Телеграм');
    expect(telegramInput.placeholder).toBe('@your_username');
  });

  it('submit button is enabled when message is filled', () => {
    component.form.setValue({
      name: '',
      email: '',
      telegram: '',
      message: 'Hello',
      personalDataConsent: true,
    });
    fixture.detectChanges();
    const button = fixture.nativeElement.querySelector(
      'button[type="submit"]',
    ) as HTMLButtonElement;
    expect(button.disabled).toBe(false);
  });

  it('requires personal data consent before submitting', () => {
    component.form.setValue({
      name: '',
      email: '',
      telegram: '',
      message: 'Hello',
      personalDataConsent: false,
    });
    fixture.detectChanges();

    component.submit();

    const button = fixture.nativeElement.querySelector(
      'button[type="submit"]',
    ) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
    expect(contactService.createContactRequest).not.toHaveBeenCalled();
  });

  it('empty optional fields are sent as null', () => {
    component.form.setValue({
      name: '',
      email: '',
      telegram: '',
      message: 'Test message',
      personalDataConsent: true,
    });
    fixture.detectChanges();

    component.submit();

    expect(contactService.createContactRequest).toHaveBeenCalledWith({
      name: null,
      email: null,
      telegram: null,
      message: 'Test message',
    });
  });

  it('whitespace-only optional fields are sent as null', () => {
    component.form.setValue({
      name: '   ',
      email: '',
      telegram: '',
      message: 'Test message',
      personalDataConsent: true,
    });
    fixture.detectChanges();

    component.submit();

    expect(contactService.createContactRequest).toHaveBeenCalledWith({
      name: null,
      email: null,
      telegram: null,
      message: 'Test message',
    });
  });

  it('non-empty optional fields are sent as string', () => {
    component.form.setValue({
      name: 'Alice',
      email: 'alice@example.com',
      telegram: '@alice',
      message: 'Hello',
      personalDataConsent: true,
    });
    fixture.detectChanges();

    component.submit();

    expect(contactService.createContactRequest).toHaveBeenCalledWith({
      name: 'Alice',
      email: 'alice@example.com',
      telegram: '@alice',
      message: 'Hello',
    });
  });

  it('displays backend validation error when present', () => {
    contactService.createContactRequest.mockReturnValue(throwError(() => mockApiError));
    component.form.setValue({
      name: '',
      email: '',
      telegram: '',
      message: 'Test',
      personalDataConsent: true,
    });
    fixture.detectChanges();

    component.submit();
    fixture.detectChanges();

    const errorEl = fixture.nativeElement.querySelector('[data-testid="submit-error"]');
    expect(errorEl).toBeTruthy();
    expect(errorEl.textContent).toContain('name');
    expect(errorEl.textContent).toContain('Ensure this field has no more than 255 characters.');
    expect(notificationService.error).toHaveBeenCalledWith('Не удалось отправить заявку.');
  });

  it('displays success state after 204 response', () => {
    contactService.createContactRequest.mockReturnValue(of(null));
    component.form.setValue({
      name: 'Alice',
      email: '',
      telegram: '',
      message: 'Test',
      personalDataConsent: true,
    });
    fixture.detectChanges();

    component.submit();
    fixture.detectChanges();

    const successEl = fixture.nativeElement.querySelector('.alert-success');
    expect(successEl).toBeTruthy();
    expect(successEl.textContent).toContain('Заявка отправлена');

    const form = fixture.nativeElement.querySelector('form');
    expect(form).toBeFalsy();
    expect(notificationService.success).toHaveBeenCalledWith('Заявка отправлена.');
  });
});
