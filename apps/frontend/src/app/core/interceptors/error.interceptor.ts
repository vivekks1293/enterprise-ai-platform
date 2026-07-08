import { inject } from '@angular/core';
import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { NotificationService } from '@core/services/notification.service';
import { LoggerService } from '@core/services/logger.service';

/**
 * Centralized HTTP error handling. Feature services/repositories
 * should not need their own try/catch boilerplate for the common
 * case — this surfaces a notification and logs, then re-throws so
 * callers can still handle specific error codes if needed.
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notifications = inject(NotificationService);
  const logger = inject(LoggerService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      logger.error(`HTTP ${error.status} on ${req.method} ${req.url}`, error);
      notifications.notify('Something went wrong. Please try again.', 'error');
      return throwError(() => error);
    })
  );
};
