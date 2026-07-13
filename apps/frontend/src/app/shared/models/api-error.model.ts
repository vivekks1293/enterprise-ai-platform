/**
 * The single error shape the rest of the app is allowed to depend on.
 * Raw HttpErrorResponse / fetch errors are normalized into this at the
 * interceptor/streaming-client boundary and never leak past it.
 * Components/Facades branch on `.kind`, never on HTTP status codes directly.
 */
export type ApiErrorKind =
  | 'network' // request never reached the server (offline, DNS, CORS)
  | 'timeout'
  | 'unauthorized' // 401
  | 'forbidden' // 403
  | 'not_found' // 404
  | 'validation' // 400 / 422
  | 'conflict' // 409
  | 'server' // 5xx
  | 'stream' // SSE/streaming-specific failure
  | 'unknown';

export interface ApiFieldError {
  readonly field: string;
  readonly message: string;
}

export interface ApiError {
  readonly kind: ApiErrorKind;
  readonly status: number | null;
  readonly message: string;
  readonly code?: string;
  readonly correlationId?: string;
  readonly fieldErrors?: readonly ApiFieldError[];
  readonly cause?: unknown;
}
