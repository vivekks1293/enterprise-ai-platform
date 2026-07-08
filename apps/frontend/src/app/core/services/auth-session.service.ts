import { Injectable, computed, signal } from '@angular/core';
import { STORAGE_KEYS } from '@core/constants/app.constants';

export interface AuthSessionUser {
  readonly id: string;
  readonly displayName: string;
  readonly email: string;
}

/**
 * Holds the current session state as a signal. This is intentionally
 * minimal — no real authentication logic, token refresh, or backend
 * calls, per project scope. The `auth` feature (see features/auth)
 * and `auth.guard.ts` are the intended future consumers of this API.
 */
@Injectable({ providedIn: 'root' })
export class AuthSessionService {
  private readonly _currentUser = signal<AuthSessionUser | null>(null);

  public readonly currentUser = this._currentUser.asReadonly();
  public readonly isAuthenticated = computed(() => this._currentUser() !== null);

  public setSession(user: AuthSessionUser, token: string): void {
    this._currentUser.set(user);
    localStorage.setItem(STORAGE_KEYS.authToken, token);
  }

  public clearSession(): void {
    this._currentUser.set(null);
    localStorage.removeItem(STORAGE_KEYS.authToken);
  }

  public getToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.authToken);
  }
}
