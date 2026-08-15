import { Citation } from '@features/chat/models/citation.model';

/**
 * The typed, chat-specific shape ChatRepository.streamPrompt() produces
 * from raw SSE frames — this is what lets ChatFacade never touch a raw
 * event name string or unparsed JSON payload at all. Mirrors the
 * generic `StreamEvent<T>` (data/streaming/stream-event.model.ts)
 * pattern of being a discriminated union designed for additive growth:
 * a future `tool_call`/`tool_result` kind is one more union member and
 * one more `case` in ChatFacade's switch, never a redesign.
 */
export type ChatStreamEvent =
  | { readonly kind: 'token'; readonly content: string }
  | { readonly kind: 'citations'; readonly citations: readonly Citation[] }
  | { readonly kind: 'complete' };
