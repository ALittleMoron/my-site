import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { AdminPanelHeaderComponent } from './admin-panel-header.component';

describe('AdminPanelHeaderComponent', () => {
  let fixture: ComponentFixture<AdminPanelHeaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminPanelHeaderComponent],
      providers: [provideRouter([]), provideI18nTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminPanelHeaderComponent);
    fixture.detectChanges();
  });

  it('renders localized title and an icon-only home link', () => {
    const homeLink = fixture.nativeElement.querySelector(
      '[data-testid="admin-panel-home-link"]',
    ) as HTMLAnchorElement;

    expect(fixture.nativeElement.textContent).toContain('Админ-панель');
    expect(homeLink.getAttribute('href')).toBe('/ru/about-me');
    expect(homeLink.getAttribute('aria-label')).toBe('На главную');
    expect(homeLink.textContent?.trim()).toBe('');
  });
});
