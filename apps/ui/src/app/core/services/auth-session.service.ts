import { Injectable, signal, computed } from '@angular/core';
import { STORAGE_KEYS } from '@core/constants/app.constants';

export interface UserSession {
  readonly id: string;
  readonly email: string;
  readonly name: string;
  readonly roleType?: number;
}

@Injectable({ providedIn: 'root' })
export class AuthSessionService {
  private readonly _user = signal<UserSession | null>(this.loadStoredUser());
  private readonly _token = signal<string | null>(localStorage.getItem(STORAGE_KEYS.authToken));

  public readonly currentUser = this._user.asReadonly();
  public readonly token = this._token.asReadonly();
  public readonly isAuthenticated = computed(() => this._token() !== null);

  public setSession(user: UserSession, token: string): void {
    this._user.set(user);
    this._token.set(token);
    localStorage.setItem(STORAGE_KEYS.authToken, token);
    localStorage.setItem(STORAGE_KEYS.authUser, JSON.stringify(user));
  }

  public clearSession(): void {
    this._user.set(null);
    this._token.set(null);
    localStorage.removeItem(STORAGE_KEYS.authToken);
    localStorage.removeItem(STORAGE_KEYS.authUser);
  }

  public getToken(): string | null {
    return this._token();
  }

  private loadStoredUser(): UserSession | null {
    const raw = localStorage.getItem(STORAGE_KEYS.authUser);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as UserSession;
    } catch {
      return null;
    }
  }
}

