import { inject } from '@angular/core';
import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { NotificationService } from '@core/services/notification.service';
import { LoggerService } from '@core/services/logger.service';
import { normalizeHttpError } from '@core/utils/api-error.util';
import { CORRELATION_ID_CONTEXT } from '@core/interceptors/correlation-id.interceptor';
import { ApiError } from '@shared/models/api-error.model';

/**
 * Centralized HTTP error handling. This is the ONE place raw
 * HttpErrorResponse objects get translated into the app-wide
 * ApiError shape (see core/utils/api-error.util.ts) — everything
 * downstream (Repositories, Facades, Components) only ever handles
 * ApiError, never HttpErrorResponse or a raw status code.
 *
 * Validation errors (400/422) are surfaced field-by-field by the form
 * that triggered them, not as a generic toast, so this intentionally
 * skips the notification for that one kind.
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notifications = inject(NotificationService);
  const logger = inject(LoggerService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      const correlationId = req.context.get(CORRELATION_ID_CONTEXT) || undefined;
      const apiError: ApiError = normalizeHttpError(error, correlationId);

      logger.error(`${apiError.kind.toUpperCase()} on ${req.method} ${req.url}`, apiError);

      if (apiError.kind !== 'validation') {
        notifications.notify(apiError.message, 'error');
      }

      return throwError(() => apiError);
    })
  );
};
