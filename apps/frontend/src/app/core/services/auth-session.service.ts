import { Injectable, computed, signal } from '@angular/core';
import { STORAGE_KEYS } from '@core/constants/app.constants';
import { storageUtil } from '@core/utils/storage.util';

export interface AuthSessionUser {
  readonly id: string;
  readonly displayName: string;
  readonly email: string;
  /** Unused by any guard/UI today — reserved so role-based
   *  authorization doesn't require a breaking change to this shape. */
  readonly roles: readonly string[];
}

/**
 * Holds the current session as a signal and is the single source of
 * truth for "who is logged in" across the whole app — the Shell reads
 * it to render the user menu, route guards read it to gate navigation,
 * and the auth interceptor reads the token from it on every request.
 *
 * Deliberately minimal compared to the auth feature's own `User`
 * domain model (features/auth/models/user.model.ts): Core only needs
 * enough to answer "who, and are they logged in" — richer profile data
 * stays feature-owned so Core never has to import from `features/`.
 *
 * Session is persisted to localStorage (via `storageUtil`, not plain
 * `localStorage`, so a malformed/legacy value degrades to "logged out"
 * instead of throwing) so a page refresh doesn't silently log the user
 * out — only the token was persisted before this sprint, which was a
 * real gap for anything relying on `currentUser` surviving a reload.
 */
@Injectable({ providedIn: 'root' })
export class AuthSessionService {
  private readonly _currentUser = signal<AuthSessionUser | null>(this.readInitialUser());
  private readonly _expiresAt = signal<Date | null>(this.readInitialExpiry());

  public readonly currentUser = this._currentUser.asReadonly();
  public readonly isAuthenticated = computed(() => this._currentUser() !== null);

  /** Placeholder — nothing currently reacts to this becoming true; reserved
   *  for silent-refresh / forced-logout-on-expiry once that flow is built. */
  public readonly isSessionExpired = computed(() => {
    const expiresAt = this._expiresAt();
    return expiresAt !== null && expiresAt.getTime() <= Date.now();
  });

  public setSession(user: AuthSessionUser, token: string, expiresAt?: Date): void {
    this._currentUser.set(user);
    this._expiresAt.set(expiresAt ?? null);
    localStorage.setItem(STORAGE_KEYS.authToken, token);
    storageUtil.setItem(STORAGE_KEYS.authUser, user);
    if (expiresAt) {
      storageUtil.setItem(STORAGE_KEYS.authExpiresAt, expiresAt.toISOString());
    }
  }

  public clearSession(): void {
    this._currentUser.set(null);
    this._expiresAt.set(null);
    localStorage.removeItem(STORAGE_KEYS.authToken);
    storageUtil.removeItem(STORAGE_KEYS.authUser);
    storageUtil.removeItem(STORAGE_KEYS.authExpiresAt);
  }

  public getToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.authToken);
  }

  private readInitialUser(): AuthSessionUser | null {
    // No token, no session — even if a stale user object were left behind.
    if (!localStorage.getItem(STORAGE_KEYS.authToken)) {
      return null;
    }
    return storageUtil.getItem<AuthSessionUser>(STORAGE_KEYS.authUser);
  }

  private readInitialExpiry(): Date | null {
    const raw = storageUtil.getItem<string>(STORAGE_KEYS.authExpiresAt);
    return raw ? new Date(raw) : null;
  }
}
