import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthSessionService } from '@core/services/auth-session.service';
import { ROUTE_PATHS } from '@core/constants/app.constants';

/**
 * Functional route guard scaffold. Real authentication logic is out
 * of scope for this sprint — this simply demonstrates the intended
 * shape so the `auth` feature can plug in without any router changes.
 */
export const authGuard: CanActivateFn = () => {
  const session = inject(AuthSessionService);
  const router = inject(Router);

  if (session.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree([`/${ROUTE_PATHS.auth.root}/${ROUTE_PATHS.auth.login}`]);
};
