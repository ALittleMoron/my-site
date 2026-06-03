import { DOCUMENT } from '@angular/common';
import { Injectable, inject, signal } from '@angular/core';

const STORAGE_KEY = 'accessToken';

@Injectable({ providedIn: 'root' })
export class AuthTokenService {
  private readonly document = inject(DOCUMENT);

  readonly token = signal<string | null>(this.storage()?.getItem(STORAGE_KEY) ?? null);

  setToken(token: string): void {
    this.storage()?.setItem(STORAGE_KEY, token);
    this.token.set(token);
  }

  clearToken(): void {
    this.storage()?.removeItem(STORAGE_KEY);
    this.token.set(null);
  }

  private storage(): Storage | null {
    return this.document.defaultView?.localStorage ?? null;
  }
}
