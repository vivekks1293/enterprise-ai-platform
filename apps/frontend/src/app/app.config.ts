import { ApplicationConfig, ErrorHandler } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { APP_ROUTES } from '@app/app.routes';
import { APP_CONFIG } from '@core/tokens/app.tokens';
import { GlobalErrorHandler } from '@core/services/global-error-handler';
import { correlationIdInterceptor } from '@core/interceptors/correlation-id.interceptor';
import { authInterceptor } from '@core/interceptors/auth.interceptor';
import { requestLoggingInterceptor } from '@core/interceptors/request-logging.interceptor';
import { errorInterceptor } from '@core/interceptors/error.interceptor';
import { environment } from '@env/environment';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(APP_ROUTES, withComponentInputBinding()),
    // Order is deliberate: correlationId stamps the request first so every
    // later interceptor (and the error interceptor's normalization) can
    // read it back; auth attaches credentials next; requestLogging observes
    // the already-fully-formed request; errorInterceptor sits closest to
    // the actual HTTP call so it normalizes failures before anything else
    // downstream sees them.
    provideHttpClient(
      withInterceptors([correlationIdInterceptor, authInterceptor, requestLoggingInterceptor, errorInterceptor])
    ),
    provideAnimations(),
    { provide: APP_CONFIG, useValue: environment },
    { provide: ErrorHandler, useClass: GlobalErrorHandler }
  ]
};
