import { Observable, delay, of, throwError } from 'rxjs';
import { AuthSession } from '@features/auth/models/auth-session.model';
import { LoginCredentials } from '@features/auth/models/login-credentials.model';
import { User } from '@features/auth/models/user.model';
import { ApiError } from '@shared/models/api-error.model';

const MOCK_USER: User = {
  id: 'u-1001',
  email: 'vivek@enterprise.ai',
  displayName: 'Vivek Kumar',
  roles: ['member']
};

const MOCK_CREDENTIALS: LoginCredentials = {
  email: 'vivek@enterprise.ai',
  password: 'password123'
};

/**
 * Mirrors what a real backend would do: succeeds only for one known
 * credential pair, otherwise fails with the same normalized ApiError
 * shape the interceptor would produce. This lets the entire
 * success/error UI be exercised end-to-end with no backend running —
 * try the wrong password and watch the real error-state path light up.
 */
export function mockLogin(credentials: LoginCredentials): Observable<AuthSession> {
  const isValid =
    credentials.email.toLowerCase() === MOCK_CREDENTIALS.email &&
    credentials.password === MOCK_CREDENTIALS.password;

  if (!isValid) {
    const error: ApiError = {
      kind: 'unauthorized',
      status: 401,
      message: 'Incorrect email or password.'
    };
    return throwError(() => error).pipe(delay(500));
  }

  const session: AuthSession = {
    user: MOCK_USER,
    accessToken: 'mock-jwt-token',
    expiresAt: new Date(Date.now() + 60 * 60 * 1000)
  };
  return of(session).pipe(delay(500));
}

export function mockLogout(): Observable<void> {
  return of(undefined).pipe(delay(200));
}
