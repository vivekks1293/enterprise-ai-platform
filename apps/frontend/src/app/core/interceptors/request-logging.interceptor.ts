import { inject } from '@angular/core';
import { HttpEvent, HttpEventType, HttpInterceptorFn } from '@angular/common/http';
import { tap } from 'rxjs';
import { LoggerService } from '@core/services/logger.service';
import { APP_CONFIG } from '@core/tokens/app.tokens';

/**
 * Development-only visibility into outgoing requests and their timing.
 * Gated on `debugMode` so it's a no-op in production builds. This is
 * the designated hook point for future request/response tracing
 * (e.g. shipping timings to a telemetry backend) without touching
 * every feature's code.
 */
export const requestLoggingInterceptor: HttpInterceptorFn = (req, next) => {
  const logger = inject(LoggerService);
  const config = inject(APP_CONFIG);

  if (!config.debugMode) {
    return next(req);
  }

  const startedAt = performance.now();

  return next(req).pipe(
    tap((event: HttpEvent<unknown>) => {
      if (event.type === HttpEventType.Response) {
        const durationMs = Math.round(performance.now() - startedAt);
        logger.info(`${req.method} ${req.urlWithParams} → ${event.status} (${durationMs}ms)`);
      }
    })
  );
};
