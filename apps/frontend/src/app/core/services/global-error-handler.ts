import { ErrorHandler, Injectable, inject } from '@angular/core';
import { LoggerService } from '@core/services/logger.service';

/**
 * Catches uncaught synchronous and async errors app-wide (outside the
 * HTTP pipeline, which is handled by error.interceptor.ts). Registered
 * in app.config.ts via `{ provide: ErrorHandler, useClass: ... }`.
 */
@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  private readonly logger = inject(LoggerService);

  public handleError(error: unknown): void {
    this.logger.error('Uncaught application error', error);
  }
}
