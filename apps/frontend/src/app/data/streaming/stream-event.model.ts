/**
 * Generic domain model for anything delivered over a live connection —
 * AI response tokens, tool-calling events, agent progress, background
 * job status, or live notifications. This is intentionally NOT
 * chat-specific: the Chat feature (future sprint) will narrow this
 * down to the event kinds it cares about, but Notifications, Agents,
 * and Document processing can all reuse the same connection lifecycle
 * and the same discriminated-union shape.
 *
 * Adding a new kind later (e.g. `tool_result`) is additive — one more
 * union member and one more `case` in whatever mapper consumes it —
 * never a redesign of the streaming layer itself.
 */
export type StreamEvent<TPayload = unknown> =
  | { readonly kind: 'open' }
  | { readonly kind: 'message'; readonly event: string; readonly data: TPayload; readonly id?: string }
  | { readonly kind: 'done' }
  | { readonly kind: 'error'; readonly error: import('@shared/models/api-error.model').ApiError };

/** Raw frame as parsed off the wire, before any domain-specific mapping. */
export interface SseFrame {
  readonly event: string;
  readonly data: string;
  readonly id?: string;
}
