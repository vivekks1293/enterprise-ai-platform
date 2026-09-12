import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthSessionService } from '@core/services/auth-session.service';
import { ROUTE_PATHS } from '@core/constants/app.constants';

export const authGuard: CanActivateFn = () => {
  const session = inject(AuthSessionService);
  const router = inject(Router);

  if (session.isAuthenticated()) {
    return true;
  }

  router.navigate([ROUTE_PATHS.login]);
  return false;
};

