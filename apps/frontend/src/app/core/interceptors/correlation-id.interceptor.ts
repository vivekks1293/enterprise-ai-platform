import { HttpContextToken, HttpInterceptorFn } from '@angular/common/http';
import { generateId } from '@core/utils/id.util';

/**
 * Lets the error interceptor read back the same correlation id that
 * was stamped onto the request, so a normalized ApiError can carry it
 * without the two interceptors needing to share any other state.
 */
export const CORRELATION_ID_CONTEXT = new HttpContextToken<string>(() => '');

/**
 * Stamps every outgoing request with a correlation id so a failure can
 * be traced end-to-end across frontend logs and backend logs once the
 * backend echoes it back. Placeholder in the sense that there's no
 * backend contract to correlate against yet — the header name and
 * generation strategy are the pieces likely to change once that
 * contract exists, and this is the only file that would need to.
 */
export const correlationIdInterceptor: HttpInterceptorFn = (req, next) => {
  const correlationId = generateId();
  req.context.set(CORRELATION_ID_CONTEXT, correlationId);

  return next(
    req.clone({
      setHeaders: { 'X-Correlation-Id': correlationId }
    })
  );
};
