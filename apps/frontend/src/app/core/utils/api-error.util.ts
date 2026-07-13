import { HttpErrorResponse } from '@angular/common/http';
import { ApiError, ApiErrorKind, ApiFieldError } from '@shared/models/api-error.model';

/**
 * The single place that knows how to read our backend's error payload
 * shape (or lack thereof) and translate HTTP status codes into
 * ApiErrorKind. If the backend's error envelope changes, this is the
 * only function that needs to change — every interceptor, repository,
 * and facade downstream keeps working unmodified.
 */
export function normalizeHttpError(error: HttpErrorResponse, correlationId?: string): ApiError {
  if (error.status === 0) {
    return {
      kind: 'network',
      status: null,
      message: 'Unable to reach the server. Check your connection and try again.',
      correlationId,
      cause: error
    };
  }

  const kind = statusToKind(error.status);
  const backendMessage = extractBackendMessage(error);
  const fieldErrors = extractFieldErrors(error);

  return {
    kind,
    status: error.status,
    message: backendMessage ?? defaultMessageForKind(kind),
    code: extractBackendCode(error),
    correlationId,
    fieldErrors,
    cause: error
  };
}

function statusToKind(status: number): ApiErrorKind {
  switch (status) {
    case 401:
      return 'unauthorized';
    case 403:
      return 'forbidden';
    case 404:
      return 'not_found';
    case 400:
    case 422:
      return 'validation';
    case 409:
      return 'conflict';
    default:
      return status >= 500 ? 'server' : 'unknown';
  }
}

function defaultMessageForKind(kind: ApiErrorKind): string {
  switch (kind) {
    case 'unauthorized':
      return 'Your session has expired. Please sign in again.';
    case 'forbidden':
      return "You don't have permission to do that.";
    case 'not_found':
      return 'The requested resource could not be found.';
    case 'validation':
      return 'Some of the submitted data was invalid.';
    case 'conflict':
      return 'This conflicts with existing data.';
    case 'server':
      return 'Something went wrong on our end. Please try again.';
    case 'timeout':
      return 'The request took too long. Please try again.';
    case 'stream':
      return 'The live connection was interrupted.';
    default:
      return 'An unexpected error occurred.';
  }
}

/** Backend error payload shape is not finalized yet — this defensively
 *  checks a couple of likely field names rather than assuming one. */
function extractBackendMessage(error: HttpErrorResponse): string | undefined {
  const body = error.error as unknown;
  if (typeof body === 'string' && body.trim()) {
    return body;
  }
  if (body && typeof body === 'object') {
    const record = body as Record<string, unknown>;
    const candidate = record['message'] ?? record['error'] ?? record['detail'];
    if (typeof candidate === 'string') {
      return candidate;
    }
  }
  return undefined;
}

function extractBackendCode(error: HttpErrorResponse): string | undefined {
  const body = error.error as unknown;
  if (body && typeof body === 'object') {
    const code = (body as Record<string, unknown>)['code'];
    if (typeof code === 'string') {
      return code;
    }
  }
  return undefined;
}

function extractFieldErrors(error: HttpErrorResponse): readonly ApiFieldError[] | undefined {
  const body = error.error as unknown;
  if (!body || typeof body !== 'object') {
    return undefined;
  }
  const errors = (body as Record<string, unknown>)['errors'];
  if (!Array.isArray(errors)) {
    return undefined;
  }
  return errors
    .filter((entry): entry is Record<string, unknown> => typeof entry === 'object' && entry !== null)
    .map((entry) => ({
      field: String(entry['field'] ?? ''),
      message: String(entry['message'] ?? '')
    }));
}
