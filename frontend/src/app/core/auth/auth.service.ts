import { Injectable, inject } from '@angular/core';
import { Observable, tap, switchMap, map } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ApiClient } from '../http/api-client.service';
import { AuthTokenService } from './auth-token.service';
import { AuthSessionService } from './auth-session.service';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
}

export interface AccountInfo {
  username: string;
  role: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly apiClient = inject(ApiClient);
  private readonly tokenService = inject(AuthTokenService);
  private readonly session = inject(AuthSessionService);

  readonly currentUser = this.session.currentUser;
  readonly isAdmin = this.session.isAdmin;
  readonly isLoggedIn = this.session.isLoggedIn;

  constructor() {
    if (this.tokenService.token()) {
      this.loadCurrentUser().pipe(takeUntilDestroyed()).subscribe();
    }
  }

  login(username: string, password: string): Observable<void> {
    return this.apiClient
      .post<LoginResponse>('/api/auth/login', { username, password } satisfies LoginRequest)
      .pipe(
        tap((response) => this.tokenService.setToken(response.accessToken)),
        switchMap(() => this.loadCurrentUser()),
      );
  }

  logout(): Observable<void> {
    return this.apiClient.post<void>('/api/auth/logout', {}).pipe(
      tap(() => {
        this.tokenService.clearToken();
        this.session.clear();
      }),
    );
  }

  clearLocalSession(): void {
    this.tokenService.clearToken();
    this.session.clear();
  }

  loadCurrentUser(): Observable<void> {
    return this.apiClient.get<AccountInfo>('/api/account/base').pipe(
      map((account) => {
        this.session.setCurrentUser(account);
      }),
    );
  }
}
