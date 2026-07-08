import { Injectable } from '@angular/core';

/**
 * Thin abstraction over console logging. Swapping to a real telemetry
 * provider (Sentry, Datadog, etc.) later only requires changing this
 * one file — no call sites elsewhere in the app need to change.
 */
@Injectable({ providedIn: 'root' })
export class LoggerService {
  public info(message: string, ...context: unknown[]): void {
    console.log(`[INFO] ${message}`, ...context);
  }

  public warn(message: string, ...context: unknown[]): void {
    console.warn(`[WARN] ${message}`, ...context);
  }

  public error(message: string, error?: unknown, ...context: unknown[]): void {
    console.error(`[ERROR] ${message}`, error, ...context);
  }
}
