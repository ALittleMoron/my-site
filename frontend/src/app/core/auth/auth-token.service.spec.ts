import { TestBed } from '@angular/core/testing';
import { DOCUMENT } from '@angular/common';
import { AuthTokenService } from './auth-token.service';

describe('AuthTokenService', () => {
  let service: AuthTokenService;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({});
    service = TestBed.inject(AuthTokenService);
  });

  afterEach(() => {
    jest.restoreAllMocks();
    localStorage.clear();
  });

  it('token is null when localStorage is empty', () => {
    expect(service.token()).toBeNull();
  });

  it('setToken stores to localStorage and updates signal', () => {
    service.setToken('test-token-123');
    expect(service.token()).toBe('test-token-123');
    expect(localStorage.getItem('accessToken')).toBe('test-token-123');
  });

  it('clearToken removes from localStorage and sets signal to null', () => {
    service.setToken('test-token-123');
    service.clearToken();
    expect(service.token()).toBeNull();
    expect(localStorage.getItem('accessToken')).toBeNull();
  });

  it('does not read localStorage when a server document has no defaultView', () => {
    jest.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('localStorage is not available on the server');
    });
    jest.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('localStorage is not available on the server');
    });
    jest.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {
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

    const serverService = TestBed.inject(AuthTokenService);

    expect(serverService.token()).toBeNull();
    serverService.setToken('ignored-on-server');
    expect(serverService.token()).toBe('ignored-on-server');
    serverService.clearToken();
    expect(serverService.token()).toBeNull();
  });
});
