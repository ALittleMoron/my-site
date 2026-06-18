import { Injectable, inject } from '@angular/core';
import {
  Observable,
  catchError,
  finalize,
  map,
  of,
  shareReplay,
  switchMap,
  tap,
  throwError,
} from 'rxjs';
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

export type AccountRole = 'anon' | 'user' | 'moderator' | 'admin';

export interface AccountInfo {
  username: string;
  role: AccountRole;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly apiClient = inject(ApiClient);
  private readonly tokenService = inject(AuthTokenService);
  private readonly session = inject(AuthSessionService);
  private currentUserLoad$: Observable<void> | null = null;

  readonly currentUser = this.session.currentUser;
  readonly isAdmin = this.session.isAdmin;
  readonly canManageContent = this.session.canManageContent;
  readonly isLoggedIn = this.session.isLoggedIn;

  constructor() {
    if (this.tokenService.token()) {
      this.ensureCurrentUserLoaded()
        .pipe(takeUntilDestroyed())
        .subscribe({ error: () => undefined });
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
      tap({
        next: () => this.clearLocalSession(),
        error: () => this.clearLocalSession(),
      }),
    );
  }

  clearLocalSession(): void {
    this.tokenService.clearToken();
    this.session.clear();
  }

  ensureCurrentUserLoaded(): Observable<void> {
    if (this.currentUser() !== null || !this.tokenService.token()) {
      return of(void 0);
    }
    if (this.currentUserLoad$ !== null) {
      return this.currentUserLoad$;
    }
    this.currentUserLoad$ = this.loadCurrentUser().pipe(
      catchError((error: unknown) => {
        this.clearLocalSession();
        return throwError(() => error);
      }),
      finalize(() => {
        this.currentUserLoad$ = null;
      }),
      shareReplay({ bufferSize: 1, refCount: true }),
    );
    return this.currentUserLoad$;
  }

  loadCurrentUser(): Observable<void> {
    return this.apiClient.get<AccountInfo>('/api/account/base').pipe(
      map((account) => {
        this.session.setCurrentUser(account);
      }),
    );
  }
}
