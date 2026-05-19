import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { SiteFooterComponent } from './site-footer.component';

describe('SiteFooterComponent', () => {
  let fixture: ComponentFixture<SiteFooterComponent>;
  let el: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SiteFooterComponent],
      providers: [provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(SiteFooterComponent);
    fixture.detectChanges();
    el = fixture.nativeElement as HTMLElement;
  });

  it('renders link to /api/docs', () => {
    const link = el.querySelector('a[href="/api/docs"]');
    expect(link).not.toBeNull();
  });

  it('renders routerLink to /sitemap', () => {
    const link = el.querySelector('a[routerLink="/sitemap"]');
    expect(link).not.toBeNull();
  });

  it('renders GitHub profile link', () => {
    const link = el.querySelector('a[href="https://github.com/ALittleMoron"]');
    expect(link).not.toBeNull();
  });

  it('renders Telegram link', () => {
    const link = el.querySelector('a[href="https://t.me/alm_dmitriy_dev"]');
    expect(link).not.toBeNull();
  });

  it('renders LinkedIn link', () => {
    const link = el.querySelector('a[href="https://www.linkedin.com/in/dmitriy-lunev/"]');
    expect(link).not.toBeNull();
  });
});
