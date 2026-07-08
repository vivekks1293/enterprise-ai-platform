import { InjectionToken } from '@angular/core';
import { AppConfig } from '@core/config/app-config.model';

/**
 * Provides the resolved AppConfig anywhere in the app via DI instead
 * of importing `environment` directly in feature/service code. This
 * keeps environment-specific values swappable and testable.
 */
export const APP_CONFIG = new InjectionToken<AppConfig>('APP_CONFIG');

/** Injectable reference to the global `window` object, for testability. */
export const WINDOW = new InjectionToken<Window>('WINDOW');
