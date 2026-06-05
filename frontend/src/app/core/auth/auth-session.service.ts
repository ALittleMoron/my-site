import { Injectable, computed, signal } from '@angular/core';
import type { AccountInfo } from './auth.service';

@Injectable({ providedIn: 'root' })
export class AuthSessionService {
  readonly currentUser = signal<AccountInfo | null>(null);
  readonly isAdmin = computed(() => this.currentUser()?.role === 'admin');
  readonly canManageContent = computed(() => {
    const role = this.currentUser()?.role;
    return role === 'admin' || role === 'moderator';
  });
  readonly isLoggedIn = computed(() => this.currentUser() !== null);

  setCurrentUser(account: AccountInfo): void {
    this.currentUser.set(account);
  }

  clear(): void {
    this.currentUser.set(null);
  }
}
