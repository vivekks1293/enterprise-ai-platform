import { Injectable, signal } from '@angular/core';
import { ApiError } from '@shared/models/api-error.model';

/**
 * Feature-local state, scoped to the auth feature's routes (not
 * root) so it resets cleanly between visits to the login page.
 *
 * Deliberately does NOT hold `isAuthenticated` or `currentUser` —
 * those live in Core's AuthSessionService and are proxied through
 * AuthFacade unchanged. Duplicating them here would create two
 * sources of truth that could disagree (e.g. after a page reload
 * restores the session but this feature-local signal hasn't been
 * touched yet).
 */
@Injectable()
export class AuthStateService {
  private readonly _isSubmitting = signal<boolean>(false);
  private readonly _error = signal<ApiError | null>(null);

  public readonly isSubmitting = this._isSubmitting.asReadonly();
  public readonly error = this._error.asReadonly();

  public setSubmitting(submitting: boolean): void {
    this._isSubmitting.set(submitting);
  }

  public setError(error: ApiError | null): void {
    this._error.set(error);
  }
}
