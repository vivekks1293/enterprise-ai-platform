/**
 * A single source citation attached to an assistant response.
 * Deliberately UI-facing (camelCase, `pageNumber` not `page_number`)
 * — matches every other domain model in this feature. Rendered by
 * MessageBubbleComponent as a simple, non-interactive source list
 * (filename + page) — no click-through to a document viewer or
 * page-level preview yet, that's a larger, separate piece of work.
 */
export interface Citation {
  readonly citationId: number;
  readonly documentId: string;
  readonly chunkId: string;
  readonly filename: string;
  readonly pageNumber: number | null;
  readonly similarityScore: number;
}
