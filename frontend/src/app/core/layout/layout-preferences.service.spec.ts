import { TestBed } from '@angular/core/testing';
import { LayoutPreferencesService } from './layout-preferences.service';

describe('LayoutPreferencesService', () => {
  let service: LayoutPreferencesService;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({});
    service = TestBed.inject(LayoutPreferencesService);
  });

  it('defaults to list layout', () => {
    expect(service.matrixLayout()).toBe('list');
  });

  it('reads stored layout on init', () => {
    localStorage.setItem('chosenLayout', 'grid');
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({});
    const freshService = TestBed.inject(LayoutPreferencesService);
    expect(freshService.matrixLayout()).toBe('grid');
  });

  it('sets layout and persists to localStorage', () => {
    service.setMatrixLayout('grid');
    expect(service.matrixLayout()).toBe('grid');
    expect(localStorage.getItem('chosenLayout')).toBe('grid');
  });
});
