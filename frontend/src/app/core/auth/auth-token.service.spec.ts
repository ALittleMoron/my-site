import { TestBed } from '@angular/core/testing';
import { AuthTokenService } from './auth-token.service';

describe('AuthTokenService', () => {
  let service: AuthTokenService;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({});
    service = TestBed.inject(AuthTokenService);
  });

  afterEach(() => {
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
});
