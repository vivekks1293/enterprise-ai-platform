import { User } from '@features/auth/models/user.model';

/**
 * What a successful login produces, before AuthFacade splits it across
 * Core's AuthSessionService (token + minimal user, for Shell/guards)
 * and its own feature state (nothing else needed once persisted).
 *
 * `expiresAt` is a placeholder consumed by no one yet — it exists so
 * silent-refresh / session-expiration handling can be added later
 * without changing this model's shape.
 */
export interface AuthSession {
  readonly user: User;
  readonly accessToken: string;
  readonly expiresAt: Date;
}
