import { TestBed } from '@angular/core/testing';
import { DOCUMENT } from '@angular/common';
import { ThemeService } from './theme.service';

describe('ThemeService', () => {
  let service: ThemeService;
  let document: Document;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({});
    service = TestBed.inject(ThemeService);
    document = TestBed.inject(DOCUMENT);
  });

  it('defaults to light theme when no preference stored', () => {
    expect(service.theme()).toBe('light');
  });

  it('reads stored theme on init', () => {
    localStorage.setItem('chosenTheme', 'dark');
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({});
    const freshService = TestBed.inject(ThemeService);
    expect(freshService.theme()).toBe('dark');
  });

  it('sets data-bs-theme attribute on document element', () => {
    service.setTheme('dark');
    expect(document.documentElement.getAttribute('data-bs-theme')).toBe('dark');
  });

  it('toggles theme', () => {
    service.setTheme('light');
    service.toggleTheme();
    expect(service.theme()).toBe('dark');
    service.toggleTheme();
    expect(service.theme()).toBe('light');
  });
});
