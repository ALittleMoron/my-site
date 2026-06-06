import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AboutPageComponent } from './about-page.component';
import { provideI18nTesting } from '../../../../testing/i18n-testing';

describe('AboutPageComponent', () => {
  let fixture: ComponentFixture<AboutPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AboutPageComponent],
      providers: [
        provideI18nTesting({
          'about.contact.email': 'Эл. почта',
          'about.contact.telegram': 'Телеграм',
        }),
        provideRouter([]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AboutPageComponent);
    fixture.detectChanges();
  });

  it('renders localized direct contact methods', () => {
    expect(fixture.nativeElement.textContent).toContain('Эл. почта');
    expect(fixture.nativeElement.textContent).toContain('dima.lunev14@gmail.com');
    expect(fixture.nativeElement.textContent).toContain('Телеграм');
    expect(fixture.nativeElement.textContent).toContain('@alm_dmitriy_dev');
  });

  it('does not render the feedback CTA or form controls', () => {
    expect(fixture.nativeElement.querySelector('[data-testid="about-contact-link"]')).toBeNull();
    expect(fixture.nativeElement.querySelector('form')).toBeNull();
    expect(fixture.nativeElement.querySelector('button[type="submit"]')).toBeNull();
    expect(fixture.nativeElement.querySelector('#contact-me-email-field')).toBeNull();
    expect(fixture.nativeElement.querySelector('#contact-me-telegram-field')).toBeNull();
    expect(fixture.nativeElement.querySelector('#contact-me-message-field')).toBeNull();
  });
});
