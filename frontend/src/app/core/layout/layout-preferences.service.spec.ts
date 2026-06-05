import { TestBed } from '@angular/core/testing';
import { DOCUMENT } from '@angular/common';
import { LayoutPreferencesService } from './layout-preferences.service';

describe('LayoutPreferencesService', () => {
  let service: LayoutPreferencesService;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({});
    service = TestBed.inject(LayoutPreferencesService);
  });

  afterEach(() => {
    jest.restoreAllMocks();
    localStorage.clear();
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

  it('does not use localStorage when a server document has no defaultView', () => {
    jest.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('localStorage is not available on the server');
    });
    jest.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('localStorage is not available on the server');
    });
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [
        {
          provide: DOCUMENT,
          useValue: {
            defaultView: null,
          },
        },
      ],
    });

    const serverService = TestBed.inject(LayoutPreferencesService);

    expect(serverService.matrixLayout()).toBe('list');
    serverService.setMatrixLayout('grid');
    expect(serverService.matrixLayout()).toBe('grid');
  });
});
