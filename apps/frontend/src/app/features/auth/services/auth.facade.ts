import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthRepository } from '@data/repositories/auth.repository';
import { AuthStateService } from '@features/auth/state/auth-state.service';
import { LoginCredentials } from '@features/auth/models/login-credentials.model';
import { AuthSessionService } from '@core/services/auth-session.service';
import { ROUTE_PATHS } from '@core/constants/app.constants';
import { ApiError } from '@shared/models/api-error.model';

/**
 * The ONLY thing LoginPageComponent and LogoutPageComponent are
 * allowed to inject. Owns the full flow:
 *
 *   Repository (data) → this Facade → AuthSessionService (Core) → UI
 *
 * This is also the one place that decides what happens after
 * login/logout succeeds (navigation) — components don't navigate
 * themselves, they just call `login()`/`logout()` and react to signals.
 */
@Injectable()
export class AuthFacade {
  private readonly repository = inject(AuthRepository);
  private readonly state = inject(AuthStateService);
  private readonly session = inject(AuthSessionService);
  private readonly router = inject(Router);

  /** Proxied straight from Core — never duplicated in feature state. */
  public readonly currentUser = this.session.currentUser;
  public readonly isAuthenticated = this.session.isAuthenticated;

  public readonly isSubmitting = this.state.isSubmitting;
  public readonly error = this.state.error;

  public login(credentials: LoginCredentials): void {
    // Prevents duplicate in-flight requests if the user double-clicks
    // Sign In or the button's [disabled] binding hasn't re-rendered yet.
    if (this.state.isSubmitting()) {
      return;
    }

    this.state.setSubmitting(true);
    this.state.setError(null);

    this.repository.login(credentials).subscribe({
      next: (authSession) => {
        this.session.setSession(
          {
            id: authSession.user.id,
            displayName: authSession.user.displayName,
            email: authSession.user.email,
            roles: authSession.user.roles
          },
          authSession.accessToken,
          authSession.expiresAt
        );
        this.state.setSubmitting(false);
        void this.router.navigateByUrl(`/${ROUTE_PATHS.dashboard}`);
      },
      error: (error: ApiError) => {
        this.state.setError(error);
        this.state.setSubmitting(false);
      }
    });
  }

  public logout(): void {
    this.repository.logout().subscribe({
      // Session is cleared client-side regardless of whether the
      // backend call succeeds — a failed logout request shouldn't be
      // able to trap the user in an authenticated-looking UI state.
      next: () => this.finishLogout(),
      error: () => this.finishLogout()
    });
  }

  private finishLogout(): void {
    this.session.clearSession();
    void this.router.navigateByUrl(`/${ROUTE_PATHS.auth.root}/${ROUTE_PATHS.auth.login}`);
  }
}
