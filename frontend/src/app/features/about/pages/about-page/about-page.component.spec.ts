import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AboutPageComponent } from './about-page.component';
import { provideI18nTesting } from '../../../../testing/i18n-testing';

const normalizeText = (value: string): string => value.replace(/\s+/g, ' ').trim();

describe('AboutPageComponent', () => {
  let fixture: ComponentFixture<AboutPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AboutPageComponent],
      providers: [
        provideI18nTesting({
          'about.contact.phone': 'Телефон',
          'about.contact.email': 'Эл. почта',
          'about.contact.telegram': 'Телеграм',
        }),
        provideRouter([]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AboutPageComponent);
    fixture.detectChanges();
  });

  it('renders localized direct contact methods with phone first', () => {
    const contactSection = fixture.nativeElement.querySelector('#mentoring-contact-me-section');
    const contactText = normalizeText(contactSection.textContent);

    expect(contactText).toContain('Телефон');
    expect(contactText).toContain('+7 (993) 673-93-92');
    expect(contactText).toContain('Телеграм');
    expect(contactText).toContain('@alm_dmitriy_dev');
    expect(contactText).toContain('Эл. почта');
    expect(contactText).toContain('d.lunev.dev@gmail.com');
    expect(contactText.indexOf('Телефон')).toBeLessThan(contactText.indexOf('Телеграм'));
    expect(contactText.indexOf('Телеграм')).toBeLessThan(contactText.indexOf('Эл. почта'));
  });

  it('renders current experience from the resume', () => {
    const pageText = normalizeText(fixture.nativeElement.textContent);

    expect(pageText).toContain('START');
    expect(pageText).toContain('05/2026');
    expect(pageText).toContain('Compel');
    expect(pageText).toContain('08/2024 - 04/2026');
    expect(pageText).toContain('Fortech');
    expect(pageText).toContain('02/2020 - 01/2021');
    expect(pageText).not.toContain('Semimall Electronics');
    expect(pageText).not.toContain('Magnit');
    expect(pageText).not.toContain('Mobicult');
  });
});
