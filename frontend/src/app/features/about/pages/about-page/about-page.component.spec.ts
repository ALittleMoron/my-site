import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { provideRouter } from '@angular/router';
import { AboutPageComponent } from './about-page.component';
import { ContactService } from '../../services/contact.service';
import { ApiError } from '../../../../core/models/api-error.model';

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

  beforeEach(async () => {
    contactService = {
      createContactRequest: jest.fn().mockReturnValue(of(null)),
    };

    await TestBed.configureTestingModule({
      imports: [AboutPageComponent],
      providers: [{ provide: ContactService, useValue: contactService }, provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(AboutPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('submit button is disabled when message is empty', () => {
    component.form.setValue({ name: '', email: '', telegram: '', message: '' });
    fixture.detectChanges();
    const button = fixture.nativeElement.querySelector(
      'button[type="submit"]',
    ) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
  });

  it('submit button is enabled when message is filled', () => {
    component.form.setValue({ name: '', email: '', telegram: '', message: 'Hello' });
    fixture.detectChanges();
    const button = fixture.nativeElement.querySelector(
      'button[type="submit"]',
    ) as HTMLButtonElement;
    expect(button.disabled).toBe(false);
  });

  it('empty optional fields are sent as null', () => {
    component.form.setValue({ name: '', email: '', telegram: '', message: 'Test message' });
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
    component.form.setValue({ name: '   ', email: '', telegram: '', message: 'Test message' });
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
    component.form.setValue({ name: '', email: '', telegram: '', message: 'Test' });
    fixture.detectChanges();

    component.submit();
    fixture.detectChanges();

    const errorEl = fixture.nativeElement.querySelector('[data-testid="submit-error"]');
    expect(errorEl).toBeTruthy();
    expect(errorEl.textContent).toContain('name');
    expect(errorEl.textContent).toContain('Ensure this field has no more than 255 characters.');
  });

  it('displays success state after 204 response', () => {
    contactService.createContactRequest.mockReturnValue(of(null));
    component.form.setValue({ name: 'Alice', email: '', telegram: '', message: 'Test' });
    fixture.detectChanges();

    component.submit();
    fixture.detectChanges();

    const successEl = fixture.nativeElement.querySelector('.alert-success');
    expect(successEl).toBeTruthy();
    expect(successEl.textContent).toContain('Заявка отправлена');

    const form = fixture.nativeElement.querySelector('form');
    expect(form).toBeFalsy();
  });
});
