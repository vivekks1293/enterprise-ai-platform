import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { AuthApiService } from '@data/api-services/auth-api.service';
import { mapLoginResponseToAuthSession, mapUserDtoToModel } from '@data/mappers/auth.mapper';
import { AuthSession } from '@features/auth/models/auth-session.model';
import { LoginCredentials } from '@features/auth/models/login-credentials.model';
import { User } from '@features/auth/models/user.model';
import { APP_CONFIG } from '@core/tokens/app.tokens';
import { mockLogin, mockLogout } from '@features/auth/services/auth.mock';

/**
 * AuthRepository stays independent of the auth implementation: today
 * it's a plain email/password REST exchange against AuthApiService.
 * Swapping to OAuth2/OIDC/Azure AD/Okta/Auth0 later means adding new
 * methods here (e.g. `loginWithProvider(provider)`) that call a
 * different AuthApiService method — `login()`'s signature and every
 * caller of it stay exactly as they are today.
 *
 * This class never touches session storage — it hands AuthSession
 * back to the Facade, which decides what to persist and where. That
 * keeps the Repository testable in complete isolation from Core.
 */
@Injectable({ providedIn: 'root' })
export class AuthRepository {
  private readonly authApi = inject(AuthApiService);
  private readonly config = inject(APP_CONFIG);

  public login(credentials: LoginCredentials): Observable<AuthSession> {
    if (this.config.enableMockData) {
      return mockLogin(credentials);
    }

    return this.authApi
      .login({ email: credentials.email, password: credentials.password })
      .pipe(map(mapLoginResponseToAuthSession));
  }

  public logout(): Observable<void> {
    if (this.config.enableMockData) {
      return mockLogout();
    }

    return this.authApi.logout();
  }

  /**
   * Placeholder — not invoked by any Facade yet. Reserved for
   * session-restore-on-reload (call once at app init if a token
   * exists but the in-memory user was lost) and silent authentication.
   */
  public getCurrentUser(): Observable<User> {
    return this.authApi.getCurrentUser().pipe(map(mapUserDtoToModel));
  }

  /**
   * Placeholder — no refresh-token flow is wired up yet. Reserved so
   * an HTTP-401-triggered refresh can be added to the error
   * interceptor later without touching this Repository's shape.
   */
  public refreshSession(): Observable<AuthSession> {
    return this.authApi.refreshSession().pipe(map(mapLoginResponseToAuthSession));
  }
}
