import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { AdminPanelPageComponent } from './admin-panel-page.component';

describe('AdminPanelPageComponent', () => {
  let fixture: ComponentFixture<AdminPanelPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminPanelPageComponent],
      providers: [provideRouter([]), provideI18nTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminPanelPageComponent);
    fixture.detectChanges();
  });

  it('renders the admin header and matrix question queue section', () => {
    expect(fixture.nativeElement.querySelector('app-admin-panel-header')).not.toBeNull();
    expect(
      fixture.nativeElement.querySelector('[data-testid="admin-panel-side-panel"]'),
    ).not.toBeNull();
    expect(fixture.nativeElement.textContent).toContain('Разделы');
    expect(fixture.nativeElement.textContent).toContain('Очередь вопросов матрицы');
  });

  it('opens and closes the mobile drawer without removing the desktop side panel', () => {
    const toggle = fixture.nativeElement.querySelector(
      '[data-testid="admin-panel-side-panel-toggle"]',
    ) as HTMLButtonElement;
    const panel = fixture.nativeElement.querySelector(
      '[data-testid="admin-panel-side-panel"]',
    ) as HTMLElement;

    expect(panel.classList).toContain('admin-panel-side-panel-open');

    toggle.click();
    fixture.detectChanges();

    expect(panel.classList).toContain('admin-panel-side-panel-closed');
    expect(panel.getAttribute('inert')).toBeNull();
    expect(panel.getAttribute('aria-hidden')).toBeNull();
  });
});
