/**
 * UI-facing user model. Deliberately richer than Core's
 * `AuthSessionUser` (core/services/auth-session.service.ts) — Core
 * only needs enough to render "who is logged in" in the Shell; this
 * feature-owned model can grow (roles, permissions, tenant, avatar
 * URL, preferences...) without Core ever needing to know about it.
 *
 * `roles` is unused today — no screen reads it — but it's here now so
 * introducing role-based authorization later is additive, not a
 * breaking change to this model.
 */
export interface User {
  readonly id: string;
  readonly email: string;
  readonly displayName: string;
  readonly roles: readonly string[];
}
