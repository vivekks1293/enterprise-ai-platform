import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { AuthSessionService } from '@core/services/auth-session.service';

/**
 * Attaches the bearer token (if present) to every outgoing request.
 * Kept separate from the error interceptor so each interceptor has a
 * single responsibility and can be composed/reordered independently.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const session = inject(AuthSessionService);
  const token = session.getToken();

  if (!token) {
    return next(req);
  }

  return next(
    req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    })
  );
};
