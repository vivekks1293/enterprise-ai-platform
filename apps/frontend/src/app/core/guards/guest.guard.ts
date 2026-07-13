import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthSessionService } from '@core/services/auth-session.service';
import { ROUTE_PATHS } from '@core/constants/app.constants';

/**
 * Mirror image of `authGuard`: redirects an already-authenticated
 * user away from unauthenticated-only routes (login) instead of
 * showing them the form again. Depends only on Core, same as
 * `authGuard` — the auth feature is never imported here.
 */
export const guestGuard: CanActivateFn = () => {
  const session = inject(AuthSessionService);
  const router = inject(Router);

  if (!session.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree([`/${ROUTE_PATHS.dashboard}`]);
};
